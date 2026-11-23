package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.judge.Language;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.Instant;
import java.util.List;

public final class SubmissionDtos {

    private SubmissionDtos() {}

    /**
     * {@code customInput}, when present on a run, executes the code once against that stdin instead of the
     * sample cases (the console's "custom testcase"). It is ignored by submit.
     */
    public record RunRequest(
            @NotNull Language language,
            @NotBlank @Size(max = 65536) String code,
            @Size(max = 20000) String customInput) {}

    /**
     * Result of a single test. For hidden cases input/expected/actual are always null so
     * that hidden tests cannot be scraped through the API.
     */
    public record CaseResult(
            int index,
            boolean sample,
            boolean passed,
            Verdict verdict,
            String input,
            String expected,
            String actual,
            String error,
            Integer timeMs,
            /** What the user's own code printed (cout, print, console.log...) before the answer; null when nothing. */
            String stdout) {}

    public record RunResponse(
            Verdict verdict,
            int passed,
            int total,
            Integer runtimeMs,
            Integer memoryKb,
            String message,
            List<CaseResult> cases,
            Long submissionId) {}

    public record SubmissionView(
            Long id,
            Language language,
            Verdict verdict,
            int passed,
            int total,
            Integer runtimeMs,
            Integer memoryKb,
            Instant createdAt,
            String code) {

        static SubmissionView from(Submission s) {
            return new SubmissionView(
                    s.getId(),
                    s.getLanguage(),
                    s.getVerdict(),
                    s.getPassedCount(),
                    s.getTotalCount(),
                    s.getRuntimeMs(),
                    s.getMemoryKb(),
                    s.getCreatedAt(),
                    s.getCode());
        }
    }

    /** One histogram bucket: values in [from, to) (the last bucket includes its upper bound). */
    public record Bin(int from, int to, int count) {}

    /**
     * How one measurement compares with other accepted submissions in the same language.
     * {@code beatsPercent} is the share of the others that were strictly worse (null with no one to compare to).
     */
    public record Distribution(Integer value, Double beatsPercent, int userBin, List<Bin> bins) {}

    public record SubmissionStats(
            Long submissionId, Language language, int sampleSize, Distribution runtime, Distribution memory) {}
}
