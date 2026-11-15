package com.sujaytumu.leetcode.problem;

import java.util.List;
import java.util.Map;

public final class ProblemDtos {

    private ProblemDtos() {}

    /** Status values: TODO, ATTEMPTED, SOLVED. Always TODO for anonymous (no client id) requests. */
    public record ProblemSummary(
            Long id,
            String slug,
            String title,
            Difficulty difficulty,
            List<String> tags,
            StatusFilter status,
            boolean bookmarked) {}

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
            boolean bookmarked) {}

    public record ProblemQuery(
            String text,
            Difficulty difficulty,
            String tag,
            StatusFilter status,
            boolean bookmarkedOnly) {}
}
