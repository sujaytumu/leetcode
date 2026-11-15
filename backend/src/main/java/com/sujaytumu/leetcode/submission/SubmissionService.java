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
import java.util.ArrayList;
import java.util.List;
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

    /** Runs against sample cases only; nothing is persisted. */
    public RunResponse run(String slug, UUID clientId, Language language, String code) {
        Problem problem = requireProblem(slug);
        rateLimiter.check(clientId);
        List<TestCase> cases = problem.getTestCases().stream().filter(TestCase::isSample).toList();
        return judge(problem, clientId, language, code, cases, false);
    }

    /** Runs against every test case and records the submission. */
    public RunResponse submit(String slug, UUID clientId, Language language, String code) {
        Problem problem = requireProblem(slug);
        rateLimiter.check(clientId);
        return judge(problem, clientId, language, code, problem.getTestCases(), true);
    }

    public List<SubmissionView> history(String slug, UUID clientId) {
        Problem problem = requireProblem(slug);
        return submissions.findTop30ByClientIdAndProblemIdOrderByCreatedAtDesc(clientId, problem.getId()).stream()
                .map(SubmissionView::from)
                .toList();
    }

    private RunResponse judge(
            Problem problem, UUID clientId, Language language, String code, List<TestCase> cases, boolean persist) {
        List<CaseResult> results = new ArrayList<>();
        Verdict verdict = Verdict.ACCEPTED;
        String message = null;
        int passed = 0;
        double maxSeconds = 0;
        boolean sawTime = false;

        for (int i = 0; i < cases.size(); i++) {
            TestCase testCase = cases.get(i);
            ExecutionResult execution = executor.execute(language, code, testCase.getInput());
            if (execution.timeSeconds() != null) {
                maxSeconds = Math.max(maxSeconds, execution.timeSeconds());
                sawTime = true;
            }
            Integer timeMs = execution.timeSeconds() == null ? null : (int) Math.round(execution.timeSeconds() * 1000);

            CaseVerdict caseVerdict = evaluate(execution, testCase);
            boolean ok = caseVerdict.verdict == Verdict.ACCEPTED;
            boolean reveal = testCase.isSample();
            results.add(new CaseResult(
                    i + 1,
                    testCase.isSample(),
                    ok,
                    caseVerdict.verdict,
                    reveal ? testCase.getInput() : null,
                    reveal ? testCase.getExpectedOutput() : null,
                    reveal ? truncate(execution.stdout(), MAX_OUTPUT_CHARS) : null,
                    reveal || caseVerdict.verdict == Verdict.COMPILE_ERROR ? caseVerdict.error : null,
                    timeMs));

            if (ok) {
                passed++;
                continue;
            }
            verdict = caseVerdict.verdict;
            message = describe(verdict, i + 1, testCase.isSample(), caseVerdict.error);
            break; // stop at the first failure: further cases add latency, not information
        }

        Integer runtimeMs = sawTime ? (int) Math.round(maxSeconds * 1000) : null;
        Long submissionId = null;
        if (persist) {
            Submission saved = submissions.save(new Submission(
                    clientId, problem.getId(), language, code, verdict, passed, cases.size(), runtimeMs));
            submissionId = saved.getId();
        }
        return new RunResponse(verdict, passed, cases.size(), runtimeMs, message, results, submissionId);
    }

    private CaseVerdict evaluate(ExecutionResult execution, TestCase testCase) {
        return switch (execution.status()) {
            case OK -> outputsMatch(execution.stdout(), testCase.getExpectedOutput())
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

    private Problem requireProblem(String slug) {
        return problems.findBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }

    private record CaseVerdict(Verdict verdict, String error) {}
}
