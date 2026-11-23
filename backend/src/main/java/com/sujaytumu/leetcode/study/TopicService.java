package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemService;
import com.sujaytumu.leetcode.problem.StatusFilter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import org.springframework.stereotype.Service;

/** Per-topic counts for the Topics page: how many problems each tag has and how many the caller solved. */
@Service
public class TopicService {

    private static final int ALL = 1000;

    public record TopicView(String tag, int total, int solved, Map<Difficulty, Integer> byDifficulty) {}

    private final ProblemService problems;

    public TopicService(ProblemService problems) {
        this.problems = problems;
    }

    public List<TopicView> topics(UUID clientId) {
        List<ProblemSummary> all = problems.search(new ProblemQuery(null, null, null, null, false), clientId, 0, ALL).items();
        Map<String, List<ProblemSummary>> byTag = new TreeMap<>();
        for (ProblemSummary problem : all) {
            for (String tag : problem.tags()) {
                byTag.computeIfAbsent(tag, key -> new ArrayList<>()).add(problem);
            }
        }
        return byTag.entrySet().stream()
                .map(entry -> view(entry.getKey(), entry.getValue()))
                .sorted(Comparator.comparingInt(TopicView::total).reversed().thenComparing(TopicView::tag))
                .toList();
    }

    private static TopicView view(String tag, List<ProblemSummary> items) {
        Map<Difficulty, Integer> byDifficulty = new EnumMap<>(Difficulty.class);
        for (Difficulty difficulty : Difficulty.values()) {
            byDifficulty.put(difficulty, 0);
        }
        int solved = 0;
        for (ProblemSummary problem : items) {
            byDifficulty.merge(problem.difficulty(), 1, Integer::sum);
            if (problem.status() == StatusFilter.SOLVED) {
                solved++;
            }
        }
        return new TopicView(tag, items.size(), solved, byDifficulty);
    }
}
