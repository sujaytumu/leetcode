package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.common.RunRateLimiter;
import com.sujaytumu.leetcode.judge.CodeExecutor;
import com.sujaytumu.leetcode.judge.CodeExecutor.ExecutionResult;
import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.problem.TestCase;
import com.sujaytumu.leetcode.submission.SubmissionDtos.CaseResult;
import com.sujaytumu.leetcode.submission.SubmissionDtos.RunResponse;
import com.sujaytumu.leetcode.submission.SubmissionDtos.SubmissionView;
import com.sujaytumu.leetcode.submission.SubmissionDtos.Distribution;
import com.sujaytumu.leetcode.submission.SubmissionDtos.SubmissionStats;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * Orchestrates judging. Deliberately not transactional: sandbox calls can take seconds and must not
 * hold a database connection. Each repository call opens its own short transaction.
 */
@Service
public class SubmissionService {

    private static final int MAX_OUTPUT_CHARS = 1_000;
    private static final int MAX_ERROR_CHARS = 2_000;

    /** Test cases are independent, so they run concurrently; a small pool keeps load on the free sandbox modest. */
    private static final ExecutorService JUDGE_POOL = Executors.newFixedThreadPool(4, runnable -> {
        Thread thread = new Thread(runnable, "judge-worker");
        thread.setDaemon(true);
        return thread;
    });

    private final ProblemRepository problems;
    private final SubmissionRepository submissions;
    private final CodeExecutor executor;
    private final RunRateLimiter rateLimiter;

    public SubmissionService(
            ProblemRepository problems,
            SubmissionRepository submissions,
            CodeExecutor executor,
            RunRateLimiter rateLimiter) {
        this.problems = problems;
        this.submissions = submissions;
        this.executor = executor;
        this.rateLimiter = rateLimiter;
    }

    /**
     * Runs against sample cases only, or once against {@code customInput} when it is non-blank.
     * Nothing is persisted either way.
     */
    public RunResponse run(String slug, UUID clientId, Language language, String code, String customInput) {
        Problem problem = requireProblem(slug);
        rateLimiter.check(clientId);
        if (customInput != null && !customInput.isBlank()) {
            return runCustom(language, code, customInput);
        }
        List<TestCase> cases = problems.findSamples(problem.getId());
        return judge(problem, clientId, language, code, cases, false);
    }

    /** Runs against every test case and records the submission. */
    public RunResponse submit(String slug, UUID clientId, Language language, String code) {
        Problem problem = requireProblemWithCases(slug);
        rateLimiter.check(clientId);
        return judge(problem, clientId, language, code, problem.getTestCases(), true);
    }

    public List<SubmissionView> history(String slug, UUID clientId) {
        Problem problem = requireProblem(slug);
        return submissions.findTop30ByClientIdAndProblemIdOrderByCreatedAtDesc(clientId, problem.getId()).stream()
                .map(SubmissionView::from)
                .toList();
    }

    /** Cap on how many accepted submissions are compared, so the histogram query stays cheap. */
    private static final int STATS_SAMPLE = 5000;

    public SubmissionStats stats(long id, UUID clientId) {
        Submission mine = submissions.findById(id)
                .filter(s -> s.getClientId().equals(clientId) && s.getVerdict() == Verdict.ACCEPTED)
                .orElseThrow(() -> new NotFoundException("No accepted submission " + id + " for this client"));
        List<Object[]> rows = submissions.findMeasurements(
                mine.getProblemId(), mine.getLanguage(), Verdict.ACCEPTED,
                org.springframework.data.domain.PageRequest.of(0, STATS_SAMPLE));
        // One measurement per user (their best), so the percentages describe people rather than re-submissions.
        java.util.Set<UUID> users = new java.util.HashSet<>();
        users.add(mine.getClientId());
        for (Object[] row : rows) {
            users.add((UUID) row[3]);
        }
        int sample = users.size();
        Distribution runtime = mine.getRuntimeMs() == null ? null
                : StatsMath.distribution(StatsMath.oneBestPerUser(rows, 1, mine.getClientId(), mine.getRuntimeMs()), mine.getRuntimeMs());
        Distribution memory = mine.getMemoryKb() == null ? null
                : StatsMath.distribution(StatsMath.oneBestPerUser(rows, 2, mine.getClientId(), mine.getMemoryKb()), mine.getMemoryKb());
        return new SubmissionStats(mine.getId(), mine.getLanguage(), sample, runtime, memory);
    }

    private RunResponse judge(
            Problem problem, UUID clientId, Language language, String code, List<TestCase> cases, boolean persist) {
        List<CaseResult> results = new ArrayList<>();
        Verdict verdict = Verdict.ACCEPTED;
        String message = null;
        int passed = 0;
        double maxSeconds = 0;
        boolean sawTime = false;
        int maxMemoryKb = 0;
        boolean sawMemory = false;

        List<ExecutionResult> executions = executeAll(language, code, cases);
        for (int i = 0; i < cases.size(); i++) {
            TestCase testCase = cases.get(i);
            ExecutionResult execution = executions.get(i);
            if (execution.timeSeconds() != null) {
                maxSeconds = Math.max(maxSeconds, execution.timeSeconds());
                sawTime = true;
            }
            if (execution.memoryKb() != null) {
                maxMemoryKb = Math.max(maxMemoryKb, execution.memoryKb());
                sawMemory = true;
            }
            Integer timeMs = execution.timeSeconds() == null ? null : (int) Math.round(execution.timeSeconds() * 1000);

            CaseVerdict caseVerdict = evaluate(execution, testCase);
            String printed = userStdout(execution.stdout());
            boolean ok = caseVerdict.verdict == Verdict.ACCEPTED;
            boolean reveal = testCase.isSample();
            results.add(new CaseResult(
                    i + 1,
                    testCase.isSample(),
                    ok,
                    caseVerdict.verdict,
                    reveal ? testCase.getInput() : null,
                    reveal ? testCase.getExpectedOutput() : null,
                    reveal ? truncate(answerOf(execution.stdout()), MAX_OUTPUT_CHARS) : null,
                    reveal || caseVerdict.verdict == Verdict.COMPILE_ERROR ? caseVerdict.error : null,
                    timeMs,
                    reveal && !printed.isEmpty() ? truncate(printed, MAX_OUTPUT_CHARS) : null));

            if (ok) {
                passed++;
                continue;
            }
            verdict = caseVerdict.verdict;
            message = describe(verdict, i + 1, testCase.isSample(), caseVerdict.error);
            break; // stop at the first failure: further cases add latency, not information
        }

        Integer runtimeMs = sawTime ? (int) Math.round(maxSeconds * 1000) : null;
        Integer memoryKb = sawMemory ? maxMemoryKb : null;
        Long submissionId = null;
        if (persist) {
            Submission saved = submissions.save(new Submission(
                    clientId, problem.getId(), language, code, verdict, passed, cases.size(), runtimeMs, memoryKb));
            submissionId = saved.getId();
        }
        return new RunResponse(verdict, passed, cases.size(), runtimeMs, memoryKb, message, results, submissionId);
    }

    /** Single execution with user-supplied stdin. There is no expected output, so "passed" means it ran cleanly. */
    private RunResponse runCustom(Language language, String code, String customInput) {
        String stdin = customInput.endsWith("\n") ? customInput : customInput + "\n";
        ExecutionResult execution = executor.execute(language, code, stdin);
        Integer timeMs = execution.timeSeconds() == null ? null : (int) Math.round(execution.timeSeconds() * 1000);

        Verdict verdict;
        String error = null;
        switch (execution.status()) {
            case OK -> verdict = Verdict.ACCEPTED;
            case COMPILE_ERROR -> {
                verdict = Verdict.COMPILE_ERROR;
                error = truncate(execution.compileOutput(), MAX_ERROR_CHARS);
            }
            case RUNTIME_ERROR -> {
                verdict = Verdict.RUNTIME_ERROR;
                error = truncate(execution.stderr(), MAX_ERROR_CHARS);
            }
            case TIME_LIMIT_EXCEEDED -> verdict = Verdict.TIME_LIMIT_EXCEEDED;
            default -> {
                verdict = Verdict.INTERNAL_ERROR;
                error = truncate(execution.stderr(), MAX_ERROR_CHARS);
            }
        }
        boolean ok = verdict == Verdict.ACCEPTED;
        String message = ok
                ? null
                : switch (verdict) {
                    case COMPILE_ERROR -> "Compilation failed.";
                    case RUNTIME_ERROR -> "Runtime error on your custom input.";
                    case TIME_LIMIT_EXCEEDED -> "Time limit exceeded on your custom input.";
                    default -> "The judge hit an internal error.";
                };
        CaseResult result = new CaseResult(
                1, true, ok, verdict, stdin, null, truncate(answerOf(execution.stdout()), MAX_OUTPUT_CHARS), error, timeMs,
                userStdout(execution.stdout()).isEmpty() ? null : truncate(userStdout(execution.stdout()), MAX_OUTPUT_CHARS));
        return new RunResponse(verdict, ok ? 1 : 0, 1, timeMs, execution.memoryKb(), message, List.of(result), null);
    }

    private List<ExecutionResult> executeAll(Language language, String code, List<TestCase> cases) {
        if (cases.isEmpty()) {
            return List.of();
        }
        // Judge the first case alone: a compile error or wrong answer there ends the run without fanning out.
        ExecutionResult first = executor.execute(language, code, cases.get(0).getInput());
        if (cases.size() == 1 || evaluate(first, cases.get(0)).verdict != Verdict.ACCEPTED) {
            return List.of(first);
        }
        List<CompletableFuture<ExecutionResult>> futures = new ArrayList<>();
        for (TestCase testCase : cases.subList(1, cases.size())) {
            String input = testCase.getInput(); // read on the request thread, before handing off
            futures.add(CompletableFuture.supplyAsync(() -> executor.execute(language, code, input), JUDGE_POOL));
        }
        List<ExecutionResult> results = new ArrayList<>();
        results.add(first);
        for (CompletableFuture<ExecutionResult> future : futures) {
            try {
                results.add(future.join());
            } catch (CompletionException ex) {
                futures.forEach(f -> f.cancel(false));
                if (ex.getCause() instanceof RuntimeException runtime) {
                    throw runtime;
                }
                throw ex;
            }
        }
        return results;
    }

    private CaseVerdict evaluate(ExecutionResult execution, TestCase testCase) {
        return switch (execution.status()) {
            case OK -> outputsMatch(answerOf(execution.stdout()), testCase.getExpectedOutput())
                    ? new CaseVerdict(Verdict.ACCEPTED, null)
                    : new CaseVerdict(Verdict.WRONG_ANSWER, null);
            case COMPILE_ERROR -> new CaseVerdict(
                    Verdict.COMPILE_ERROR, truncate(execution.compileOutput(), MAX_ERROR_CHARS));
            case RUNTIME_ERROR -> new CaseVerdict(
                    Verdict.RUNTIME_ERROR, truncate(execution.stderr(), MAX_ERROR_CHARS));
            case TIME_LIMIT_EXCEEDED -> new CaseVerdict(Verdict.TIME_LIMIT_EXCEEDED, null);
            case INTERNAL_ERROR -> new CaseVerdict(
                    Verdict.INTERNAL_ERROR, truncate(execution.stderr(), MAX_ERROR_CHARS));
        };
    }

    /**
     * The generated program prints this marker right after the user's function returns, so anything the user's own
     * code printed (debug output) comes before it and the answer after it, like LeetCode's separate "Stdout" box.
     * Output without the marker (older clients, custom programs) is all answer.
     */
    static final char ANSWER_MARKER = '\u001e';

    /** The answer part of a program's stdout: everything after the last marker, or all of it without one. */
    static String answerOf(String stdout) {
        if (stdout == null) {
            return "";
        }
        int at = stdout.lastIndexOf(ANSWER_MARKER);
        return at < 0 ? stdout : stdout.substring(at + 1);
    }

    /** What the user's code printed before the answer (empty when nothing or when there is no marker). */
    static String userStdout(String stdout) {
        if (stdout == null) {
            return "";
        }
        int at = stdout.lastIndexOf(ANSWER_MARKER);
        return at < 0 ? "" : stdout.substring(0, at).stripTrailing();
    }

    /** Compares ignoring line-ending style and trailing whitespace on each line and at the end. */
    static boolean outputsMatch(String actual, String expected) {
        return normalize(actual).equals(normalize(expected));
    }

    private static String normalize(String value) {
        if (value == null) {
            return "";
        }
        String[] lines = value.replace("\r\n", "\n").replace('\r', '\n').split("\n", -1);
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < lines.length; i++) {
            if (i > 0) {
                out.append('\n');
            }
            out.append(lines[i].stripTrailing());
        }
        return out.toString().stripTrailing();
    }

    private static String describe(Verdict verdict, int caseNumber, boolean sample, String error) {
        String which = sample ? "sample case " + caseNumber : "hidden test case " + caseNumber;
        return switch (verdict) {
            case WRONG_ANSWER -> "Wrong answer on " + which + ".";
            case RUNTIME_ERROR -> "Runtime error on " + which + ".";
            case TIME_LIMIT_EXCEEDED -> "Time limit exceeded on " + which + ".";
            case COMPILE_ERROR -> "Compilation failed.";
            case INTERNAL_ERROR -> "The judge hit an internal error on " + which + ".";
            case ACCEPTED -> null;
        };
    }

    private static String truncate(String value, int max) {
        if (value == null) {
            return null;
        }
        return value.length() <= max ? value : value.substring(0, max) + "…";
    }

    /** The problem without its test cases: enough for everything except submitting. */
    private Problem requireProblem(String slug) {
        return problems.findLightBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }

    /** The problem with every test case (hidden ones included), needed to judge a submission. */
    private Problem requireProblemWithCases(String slug) {
        return problems.findBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }

    private record CaseVerdict(Verdict verdict, String error) {}
}
