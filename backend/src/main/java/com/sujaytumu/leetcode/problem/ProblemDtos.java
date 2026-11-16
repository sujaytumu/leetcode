package com.sujaytumu.leetcode.problem;

import java.util.List;
import java.util.Map;

public final class ProblemDtos {

    private ProblemDtos() {}

    /**
     * Status values: TODO, ATTEMPTED, SOLVED (always TODO for anonymous requests). {@code acceptance} is the
     * percentage of all submissions on this server that were accepted, or null when nobody has submitted yet.
     * {@code number} is the problem's position in the study path (what the UI shows as its number).
     */
    public record ProblemSummary(
            Long id,
            String slug,
            String title,
            Difficulty difficulty,
            List<String> tags,
            StatusFilter status,
            boolean bookmarked,
            Double acceptance,
            Integer number) {}

    public record SampleCase(String input, String expectedOutput) {}

    public record ProblemDetail(
            Long id,
            String slug,
            String title,
            Difficulty difficulty,
            List<String> tags,
            String description,
            Map<String, String> starterCode,
            List<SampleCase> samples,
            StatusFilter status,
            boolean bookmarked,
            Double acceptance,
            Integer number) {}

    public record ProblemQuery(
            String text,
            Difficulty difficulty,
            String tag,
            StatusFilter status,
            boolean bookmarkedOnly) {}
}
