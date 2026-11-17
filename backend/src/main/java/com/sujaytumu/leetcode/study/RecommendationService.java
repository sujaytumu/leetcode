package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemService;
import com.sujaytumu.leetcode.problem.StatusFilter;
import com.sujaytumu.leetcode.submission.Verdict;
import java.time.Duration;
import java.time.Instant;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * "For you": what to solve next, what was attempted but never solved, and old solves worth revisiting.
 * Everything is derived from the caller's own submission history.
 */
@Service
public class RecommendationService {

    static final int REVISIT_AFTER_DAYS = 7;
    static final int LIMIT = 6;
    private static final int ALL = 1000;

    public record Recommendation(ProblemSummary problem, String reason) {}

    public record Recommendations(
            List<Recommendation> next, List<Recommendation> unfinished, List<Recommendation> revisit) {}

    private record Scored(ProblemSummary problem, double score, String reason) {}

    private final ProblemService problems;
    private final SubmissionActivityRepository activity;

    public RecommendationService(ProblemService problems, SubmissionActivityRepository activity) {
        this.problems = problems;
        this.activity = activity;
    }

    @Transactional(readOnly = true)
    public Recommendations recommend(UUID clientId, Instant now) {
        List<ProblemSummary> all = problems.search(new ProblemQuery(null, null, null, null, false), clientId, 0, ALL).items();

        Map<Long, Instant> lastSolved = new HashMap<>();
        for (Object[] row : activity.lastTimePerProblem(clientId, Verdict.ACCEPTED)) {
            lastSolved.put((Long) row[0], (Instant) row[1]);
        }

        Map<String, int[]> tagStats = new HashMap<>(); // tag -> [solved, total]
        int easySolved = 0;
        int mediumSolved = 0;
        for (ProblemSummary problem : all) {
            boolean solved = problem.status() == StatusFilter.SOLVED;
            for (String tag : problem.tags()) {
                int[] stats = tagStats.computeIfAbsent(tag, key -> new int[2]);
                stats[1]++;
                if (solved) {
                    stats[0]++;
                }
            }
            if (solved && problem.difficulty() == Difficulty.EASY) {
                easySolved++;
            } else if (solved && problem.difficulty() == Difficulty.MEDIUM) {
                mediumSolved++;
            }
        }

        // Unlock harder problems as the easier tier gets comfortable.
        Set<Difficulty> allowed = EnumSet.of(Difficulty.EASY);
        if (easySolved >= 5) {
            allowed.add(Difficulty.MEDIUM);
        }
        if (mediumSolved >= 10) {
            allowed.add(Difficulty.HARD);
        }
        Difficulty stretch = allowed.stream().max(Comparator.naturalOrder()).orElse(Difficulty.EASY);

        List<Recommendation> next = all.stream()
                .filter(p -> p.status() == StatusFilter.TODO && allowed.contains(p.difficulty()))
                .map(p -> score(p, tagStats, stretch))
                .sorted(Comparator.comparingDouble(Scored::score)
                        .reversed()
                        .thenComparingInt(s -> numberOf(s.problem())))
                .limit(LIMIT)
                .map(s -> new Recommendation(s.problem(), s.reason()))
                .toList();

        List<Recommendation> unfinished = all.stream()
                .filter(p -> p.status() == StatusFilter.ATTEMPTED)
                .sorted(Comparator.comparingInt(RecommendationService::numberOf))
                .limit(LIMIT)
                .map(p -> new Recommendation(p, "Attempted, not solved yet"))
                .toList();

        List<Recommendation> revisit = all.stream()
                .filter(p -> p.status() == StatusFilter.SOLVED && lastSolved.containsKey(p.id()))
                .filter(p -> daysSince(lastSolved.get(p.id()), now) >= REVISIT_AFTER_DAYS)
                .sorted(Comparator.comparing((ProblemSummary p) -> lastSolved.get(p.id())))
                .limit(LIMIT)
                .map(p -> new Recommendation(p, "Solved " + daysSince(lastSolved.get(p.id()), now) + " days ago, worth a refresh"))
                .toList();

        return new Recommendations(next, unfinished, revisit);
    }

    private static Scored score(ProblemSummary problem, Map<String, int[]> tagStats, Difficulty stretch) {
        String bestTag = null;
        double bestRatio = 0;
        for (String tag : problem.tags()) {
            int[] stats = tagStats.get(tag);
            if (stats != null && stats[0] > 0 && stats[0] < stats[1]) {
                double ratio = stats[0] / (double) stats[1];
                if (ratio > bestRatio) {
                    bestRatio = ratio;
                    bestTag = tag;
                }
            }
        }
        double score = (bestTag != null ? 1 + bestRatio : 0) + (problem.difficulty() == stretch ? 0.5 : 0);
        String reason;
        if (bestTag != null) {
            int[] stats = tagStats.get(bestTag);
            reason = "Continue " + label(bestTag) + " (" + stats[0] + "/" + stats[1] + " solved)";
        } else if (problem.difficulty() == stretch) {
            reason = "A good stretch at your level";
        } else {
            reason = "Build a solid base";
        }
        return new Scored(problem, score, reason);
    }

    static long daysSince(Instant then, Instant now) {
        return Duration.between(then, now).toDays();
    }

    private static int numberOf(ProblemSummary problem) {
        return problem.number() != null ? problem.number() : Math.toIntExact(problem.id());
    }

    private static String label(String tag) {
        StringBuilder out = new StringBuilder();
        for (String word : tag.split("-")) {
            if (!word.isEmpty()) {
                out.append(out.length() > 0 ? " " : "").append(Character.toUpperCase(word.charAt(0))).append(word.substring(1));
            }
        }
        return out.toString();
    }
}
