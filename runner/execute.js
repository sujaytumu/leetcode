// Sandboxed execution of user code against a list of test cases.
//
// NOTE: this runs user code with plain OS limits (timeout, ulimit, process
// group kill, throwaway working directory). It is suitable for local
// development and for verifying the bundled solutions. Before exposing it to
// untrusted users on the internet, run it inside a container or microVM with
// no network access.
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { LANGS, cleanErrors } = require("./lang");
const { compare } = require("./compare");

const MAX_OUTPUT = 4 * 1024 * 1024;

function runProc(cmd, cwd, { timeoutMs, vmKb, maxOut = MAX_OUTPUT }) {
  return new Promise((resolve) => {
    const limits = [];
    if (vmKb) limits.push(`ulimit -v ${vmKb}`);
    limits.push("ulimit -s unlimited 2>/dev/null || true", "ulimit -f 65536", "ulimit -u 512 2>/dev/null || true");
    const script = `${limits.join("; ")}; exec "$@"`;
    const child = spawn("bash", ["-c", script, "sandbox", ...cmd], {
      cwd,
      detached: true,
      env: { PATH: process.env.PATH, HOME: cwd, LANG: "C.UTF-8", JAVA_TOOL_OPTIONS: "" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let timedOut = false;
    const kill = () => {
      try {
        process.kill(-child.pid, "SIGKILL");
      } catch (_) {}
    };
    const timer = setTimeout(() => {
      timedOut = true;
      kill();
    }, timeoutMs);
    child.stdout.on("data", (d) => {
      if (stdout.length < maxOut) stdout += d;
    });
    child.stderr.on("data", (d) => {
      if (stderr.length < maxOut) stderr += d;
    });
    child.on("close", (code, signal) => {
      clearTimeout(timer);
      kill();
      resolve({ code, signal, stdout, stderr, timedOut });
    });
  });
}

function readResults(file) {
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((l) => {
      try {
        return JSON.parse(l);
      } catch (_) {
        return { ok: false, err: "Output could not be parsed" };
      }
    });
}

/**
 * @param {string} lang       "python" | "cpp" | "java"
 * @param {string} code       user solution source
 * @param {object} sig        problem signature
 * @param {Array}  tests      [{ input: {param: value}, expected: any }]
 * @param {object} opts       { timeLimitMs, compare, stopOnFail }
 */
async function execute(lang, code, sig, tests, opts = {}) {
  const L = LANGS[lang];
  if (!L) return { status: "Internal Error", message: `Unsupported language: ${lang}` };
  const timeLimitMs = opts.timeLimitMs || 4000;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lc-run-"));
  try {
    const plan = L.build(sig, code);
    for (const [name, content] of Object.entries(plan.files)) fs.writeFileSync(path.join(dir, name), content);
    fs.writeFileSync(path.join(dir, "tests.json"), JSON.stringify(tests.map((t) => t.input)));
    if (lang === "java") fs.mkdirSync(path.join(dir, "out"));

    if (plan.compile) {
      const c = await runProc(plan.compile, dir, { timeoutMs: 60000, vmKb: 0 });
      if (c.code !== 0) {
        return { status: "Compile Error", message: cleanErrors(c.stderr || c.stdout, dir), passed: 0, total: tests.length };
      }
    }

    const wall = timeLimitMs * tests.length + 3000;
    const started = Date.now();
    const r = await runProc(plan.run, dir, { timeoutMs: wall, vmKb: plan.limitVirtualMemory ? 2 * 1024 * 1024 : 0 });
    const runtimeMs = Date.now() - started;
    const results = readResults(path.join(dir, "results.jsonl"));

    const cases = [];
    let passed = 0;
    let maxMs = 0;
    for (let i = 0; i < tests.length; i++) {
      const res = results[i];
      const t = tests[i];
      if (!res) {
        // The process died or timed out before reaching this test.
        const status = r.timedOut ? "Time Limit Exceeded" : r.signal || r.code ? "Runtime Error" : "Runtime Error";
        const msg = r.timedOut
          ? "Your code took too long and was stopped."
          : cleanErrors(r.stderr, dir) || `Process exited unexpectedly (${r.signal || "code " + r.code}).`;
        cases.push({ index: i, status, input: t.input, expected: t.expected, message: msg });
        break;
      }
      if (!res.ok) {
        cases.push({ index: i, status: "Runtime Error", input: t.input, expected: t.expected, message: cleanErrors(res.err, dir) });
        break;
      }
      maxMs = Math.max(maxMs, res.ms || 0);
      const slow = res.ms > timeLimitMs;
      const ok = compare(t.expected, res.out, opts.compare || "exact");
      if (slow) {
        cases.push({ index: i, status: "Time Limit Exceeded", input: t.input, expected: t.expected, output: res.out, message: `Took ${res.ms.toFixed(0)} ms (limit ${timeLimitMs} ms).` });
        break;
      }
      if (ok) {
        passed++;
        cases.push({ index: i, status: "Accepted", input: t.input, expected: t.expected, output: res.out, ms: res.ms });
      } else {
        cases.push({ index: i, status: "Wrong Answer", input: t.input, expected: t.expected, output: res.out, ms: res.ms });
        if (opts.stopOnFail !== false) break;
      }
    }

    const failed = cases.find((c) => c.status !== "Accepted");
    return {
      status: failed ? failed.status : "Accepted",
      passed,
      total: tests.length,
      runtimeMs: Math.round(maxMs),
      wallMs: runtimeMs,
      cases,
      failed: failed || null,
      stderr: cleanErrors(r.stderr, dir).slice(0, 2000),
    };
  } catch (e) {
    return { status: "Internal Error", message: String(e && e.message ? e.message : e), passed: 0, total: tests.length };
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

module.exports = { execute };
