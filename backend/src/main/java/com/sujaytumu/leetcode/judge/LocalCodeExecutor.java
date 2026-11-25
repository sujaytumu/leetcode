package com.sujaytumu.leetcode.judge;

import com.sujaytumu.leetcode.common.ApiExceptions.ExecutionUnavailableException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

/**
 * Runs code with the compilers and interpreters installed on this server (g++, javac, python3, node), as child
 * processes. Opt-in (EXEC_LOCAL=true): it is the zero-setup alternative to a Judge0 instance.
 *
 * <p>Isolation is best effort, not a full sandbox: the child gets an empty environment (no database or API secrets),
 * runs as an unprivileged user when {@code runAs} is set (the Docker image creates one), has CPU, file-size, process
 * and, for C++, address-space limits, a wall-clock kill, and capped output. Compiled programs are cached briefly so
 * the many test cases of one submission compile once.
 */
public class LocalCodeExecutor implements CodeExecutor {

    private static final int MAX_OUTPUT_BYTES = 1 << 20;
    private static final int MAX_DIAGNOSTIC_CHARS = 4000;
    private static final int CACHE_SIZE = 8;
    private static final long COMPILE_TIMEOUT_SECONDS = 60;
    private static final long SLOT_WAIT_SECONDS = 45;

    private final double cpuTimeLimitSeconds;
    private final String runAs;
    private final Semaphore runSlots = new Semaphore(Math.max(2, Runtime.getRuntime().availableProcessors()), true);
    private final Semaphore compileSlots = new Semaphore(1, true);
    private final Map<String, Object> keyLocks = new ConcurrentHashMap<>();
    private final Map<String, Compiled> cache = new LinkedHashMap<>(16, 0.75f, true);

    public LocalCodeExecutor(double cpuTimeLimitSeconds, String runAs) {
        this.cpuTimeLimitSeconds = cpuTimeLimitSeconds;
        this.runAs = runAs == null || runAs.isBlank() ? null : runAs.trim();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            synchronized (cache) {
                cache.values().forEach(c -> deleteTree(c.dir));
            }
        }, "exec-cleanup"));
    }

    /** A compiled (or, for interpreters, just written) program on disk, shared by concurrent runs of the same code. */
    private static final class Compiled {
        final Path dir;
        final String failure; // compiler output when compilation failed, else null
        int refs;
        boolean evicted;

        Compiled(Path dir, String failure) {
            this.dir = dir;
            this.failure = failure;
        }
    }

    private record Spec(String file, List<String> compile, List<String> run, String tool) {}

    private static Spec specFor(Language language) {
        return switch (language) {
            case CPP -> new Spec("Main.cpp",
                    List.of("g++", "-O2", "-std=c++17", "-pipe", "-o", "main", "Main.cpp"), List.of("./main"), "g++");
            case JAVA -> new Spec("Main.java",
                    List.of("javac", "-J-Xmx256m", "-encoding", "UTF-8", "Main.java"),
                    List.of("java", "-Xmx256m", "-Xss64m", "-XX:+UseSerialGC", "-XX:TieredStopAtLevel=1", "Main"), "javac");
            case PYTHON -> new Spec("main.py", List.of(), List.of("python3", "main.py"), "python3");
            case JAVASCRIPT -> new Spec("main.js", List.of(), List.of("node", "main.js"), "node");
        };
    }

    @Override
    public ExecutionResult execute(Language language, String sourceCode, String stdin) {
        Spec spec = specFor(language);
        if (!onPath(spec.tool())) {
            throw new ExecutionUnavailableException(
                    language.label() + " is not installed on this server (missing " + spec.tool() + ").");
        }
        String source = sourceCode == null ? "" : sourceCode;
        String key = hash(language.key() + "\0" + source);

        Compiled compiled = acquire(key, language, spec, source);
        try {
            if (compiled.failure != null) {
                return new ExecutionResult(Status.COMPILE_ERROR, "", "", compiled.failure, null);
            }
            return run(language, spec, compiled.dir, stdin == null ? "" : stdin);
        } finally {
            release(key, compiled);
        }
    }

    // ---- compile cache ----

    private Compiled acquire(String key, Language language, Spec spec, String source) {
        Object lock = keyLocks.computeIfAbsent(key, k -> new Object());
        synchronized (lock) {
            synchronized (cache) {
                Compiled hit = cache.get(key);
                if (hit != null) {
                    hit.refs++;
                    return hit;
                }
            }
            Compiled fresh = build(language, spec, source);
            fresh.refs = 1;
            synchronized (cache) {
                cache.put(key, fresh);
                trim();
            }
            return fresh;
        }
    }

    private void release(String key, Compiled compiled) {
        boolean delete;
        synchronized (cache) {
            compiled.refs--;
            delete = compiled.evicted && compiled.refs <= 0;
        }
        if (delete) {
            deleteTree(compiled.dir);
            keyLocks.remove(key);
        }
    }

    /** Called with the cache lock held: evicts least recently used entries beyond the limit. */
    private void trim() {
        Iterator<Map.Entry<String, Compiled>> it = cache.entrySet().iterator();
        while (cache.size() > CACHE_SIZE && it.hasNext()) {
            Map.Entry<String, Compiled> eldest = it.next();
            Compiled c = eldest.getValue();
            if (c.refs > 0) {
                continue;
            }
            c.evicted = true;
            it.remove();
            deleteTree(c.dir);
            keyLocks.remove(eldest.getKey());
        }
    }

    private Compiled build(Language language, Spec spec, String source) {
        acquireSlot(compileSlots, "compiling");
        Path dir = null;
        try {
            dir = Files.createTempDirectory("lcrun-");
            // The unprivileged runner user must be able to read, create and execute files here.
            Files.setPosixFilePermissions(dir, PosixFilePermissions.fromString("rwxrwxrwx"));
            Files.writeString(dir.resolve(spec.file()), source, StandardCharsets.UTF_8);
            Files.setPosixFilePermissions(dir.resolve(spec.file()), PosixFilePermissions.fromString("rw-rw-rw-"));
            if (spec.compile().isEmpty()) {
                return new Compiled(dir, null);
            }
            Proc p = exec(command(spec.compile(), COMPILE_TIMEOUT_SECONDS, 0, language == Language.CPP, true), dir, "",
                    COMPILE_TIMEOUT_SECONDS + 5);
            if (p.exit == 0 && !p.timedOut) {
                return new Compiled(dir, null);
            }
            String text = (p.stderr + p.stdout).replace(dir.toString() + "/", "");
            if (p.timedOut) {
                text = "Compilation timed out.\n" + text;
            }
            deleteTree(dir);
            return new Compiled(null, clip(text.isBlank() ? "Compilation failed." : text));
        } catch (IOException ex) {
            deleteTree(dir);
            throw new ExecutionUnavailableException("Could not prepare the program for execution.", ex);
        } finally {
            compileSlots.release();
        }
    }

    // ---- running ----

    private ExecutionResult run(Language language, Spec spec, Path dir, String stdin) {
        acquireSlot(runSlots, "running");
        try {
            boolean heavyRuntime = language == Language.JAVA || language == Language.JAVASCRIPT;
            double cpu = heavyRuntime ? cpuTimeLimitSeconds * 3 : cpuTimeLimitSeconds;
            long wall = (long) Math.ceil(cpuTimeLimitSeconds * (heavyRuntime ? 5 : 3));
            long started = System.nanoTime();
            Proc p = exec(command(spec.run(), wall, (long) Math.ceil(cpu) + 1, language == Language.CPP, false), dir, stdin,
                    wall + 2);
            double seconds = (System.nanoTime() - started) / 1e9;
            double time = Math.round(seconds * 1000) / 1000.0;

            // 124 = timeout, 137 = SIGKILL, 152 = SIGXCPU (CPU limit): all mean the program ran too long.
            if (p.timedOut || p.exit == 124 || p.exit == 137 || p.exit == 152) {
                return new ExecutionResult(Status.TIME_LIMIT_EXCEEDED, p.stdout, p.stderr, "", time);
            }
            if (p.exit != 0) {
                String detail = p.stderr.isBlank() ? describeExit(p.exit) : clip(p.stderr);
                return new ExecutionResult(Status.RUNTIME_ERROR, p.stdout, detail, "", time);
            }
            return new ExecutionResult(Status.OK, p.stdout, clip(p.stderr), "", time);
        } finally {
            runSlots.release();
        }
    }

    private static String describeExit(int exit) {
        if (exit > 128) {
            return "Runtime error (signal " + (exit - 128) + (exit == 139 ? ", segmentation fault" : "") + ").";
        }
        return "Runtime error (exit code " + exit + ").";
    }

    /** timeout [-s KILL] wall  [setpriv ...]  [prlimit ...]  command, built only from tools that exist on this host. */
    private List<String> command(List<String> argv, long wallSeconds, long cpuSeconds, boolean limitAddressSpace, boolean compile) {
        List<String> cmd = new ArrayList<>();
        if (onPath("timeout")) {
            cmd.addAll(List.of("timeout", "-s", "KILL", Long.toString(wallSeconds)));
        }
        if (runAs != null && onPath("setpriv")) {
            cmd.addAll(List.of("setpriv", "--reuid=" + runAs, "--regid=" + runAs, "--clear-groups"));
        }
        if (onPath("prlimit")) {
            cmd.add("prlimit");
            if (cpuSeconds > 0) {
                cmd.add("--cpu=" + cpuSeconds);
            }
            cmd.add("--fsize=" + (compile ? 268_435_456L : 16_777_216L));
            cmd.add("--core=0");
            if (limitAddressSpace && !compile) {
                cmd.add("--as=1073741824");
            }
            if (runAs != null) {
                cmd.add("--nproc=" + (compile ? 256 : 64));
            }
        }
        cmd.addAll(argv);
        return cmd;
    }

    private record Proc(int exit, String stdout, String stderr, boolean timedOut) {}

    private Proc exec(List<String> command, Path dir, String stdin, long waitSeconds) {
        ProcessBuilder pb = new ProcessBuilder(command).directory(dir.toFile());
        Map<String, String> env = pb.environment();
        env.clear(); // never hand the app's secrets (database password, API keys) to submitted code
        env.put("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin");
        env.put("HOME", dir.toString());
        env.put("TMPDIR", dir.toString());
        env.put("LANG", "C.UTF-8");
        Process process;
        try {
            process = pb.start();
        } catch (IOException ex) {
            throw new ExecutionUnavailableException("Could not start the program: " + ex.getMessage(), ex);
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        Thread outReader = pump(process.getInputStream(), out);
        Thread errReader = pump(process.getErrorStream(), err);
        Thread writer = new Thread(() -> {
            try (OutputStream in = process.getOutputStream()) {
                in.write(stdin.getBytes(StandardCharsets.UTF_8));
            } catch (IOException ignored) {
                // the program may exit without reading all of its input
            }
        }, "exec-stdin");
        writer.setDaemon(true);
        writer.start();

        boolean finished;
        try {
            finished = process.waitFor(waitSeconds, TimeUnit.SECONDS);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            finished = false;
        }
        if (!finished) {
            kill(process);
        }
        joinQuietly(outReader);
        joinQuietly(errReader);
        int exit = finished ? process.exitValue() : 137;
        return new Proc(exit, text(out), text(err), !finished);
    }

    private static void kill(Process process) {
        process.descendants().forEach(ProcessHandle::destroyForcibly);
        process.destroyForcibly();
    }

    private static Thread pump(InputStream stream, ByteArrayOutputStream sink) {
        Thread t = new Thread(() -> {
            byte[] buf = new byte[8192];
            try (InputStream in = stream) {
                int n;
                while ((n = in.read(buf)) >= 0) {
                    if (sink.size() < MAX_OUTPUT_BYTES) {
                        sink.write(buf, 0, Math.min(n, MAX_OUTPUT_BYTES - sink.size()));
                    } // past the cap keep draining so the program is never blocked on a full pipe
                }
            } catch (IOException ignored) {
                // stream closed when the process was killed
            }
        }, "exec-pump");
        t.setDaemon(true);
        t.start();
        return t;
    }

    private static void joinQuietly(Thread t) {
        try {
            t.join(2000);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        }
    }

    private static String text(ByteArrayOutputStream stream) {
        return stream.toString(StandardCharsets.UTF_8);
    }

    // ---- helpers ----

    private static void acquireSlot(Semaphore slots, String what) {
        try {
            if (!slots.tryAcquire(SLOT_WAIT_SECONDS, TimeUnit.SECONDS)) {
                throw new ExecutionUnavailableException("The server is busy " + what + " other submissions. Try again shortly.");
            }
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new ExecutionUnavailableException("Interrupted while waiting to run your code.", ex);
        }
    }

    private static String clip(String text) {
        return text.length() <= MAX_DIAGNOSTIC_CHARS ? text : text.substring(0, MAX_DIAGNOSTIC_CHARS) + "\n...";
    }

    private static String hash(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (java.security.NoSuchAlgorithmException ex) {
            throw new IllegalStateException(ex);
        }
    }

    private static boolean onPath(String tool) {
        String path = System.getenv("PATH");
        for (String part : (path == null ? "/usr/bin:/bin:/usr/local/bin" : path).split(":")) {
            if (!part.isEmpty() && Files.isExecutable(Path.of(part, tool))) {
                return true;
            }
        }
        return false;
    }

    private static void deleteTree(Path dir) {
        if (dir == null) {
            return;
        }
        try (Stream<Path> walk = Files.walk(dir)) {
            walk.sorted(java.util.Comparator.reverseOrder()).forEach(p -> p.toFile().delete());
        } catch (IOException ignored) {
            // best effort; the OS temp cleaner will catch leftovers
        }
    }

    @Override
    public Health health() {
        List<String> missing = new ArrayList<>();
        for (Language language : Language.values()) {
            if (!onPath(specFor(language).tool())) {
                missing.add(language.label());
            }
        }
        if (missing.size() == Language.values().length) {
            return new Health(true, false, "local", "No compilers are installed on this server.");
        }
        return new Health(true, true, "local",
                missing.isEmpty() ? "Code execution is available." : "Code execution is available (not installed: " + String.join(", ", missing) + ").");
    }
}
