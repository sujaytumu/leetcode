package com.sujaytumu.leetcode.progress;

import com.sujaytumu.leetcode.bookmark.BookmarkRepository;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import com.sujaytumu.leetcode.submission.Verdict;
import java.util.EnumMap;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProgressService {

    public record DifficultyProgress(long total, long solved) {}

    public record ProgressSummary(
            long total, long solved, long attempted, long bookmarked, Map<Difficulty, DifficultyProgress> byDifficulty) {}

    private final ProblemRepository problems;
    private final SubmissionRepository submissions;
    private final BookmarkRepository bookmarks;

    public ProgressService(
            ProblemRepository problems, SubmissionRepository submissions, BookmarkRepository bookmarks) {
        this.problems = problems;
        this.submissions = submissions;
        this.bookmarks = bookmarks;
    }

    @Transactional(readOnly = true)
    public ProgressSummary summary(UUID clientId) {
        Map<Difficulty, Long> totals = new EnumMap<>(Difficulty.class);
        for (Object[] row : problems.countByDifficulty()) {
            totals.put((Difficulty) row[0], (Long) row[1]);
        }
        Map<Difficulty, Long> solvedBy = new EnumMap<>(Difficulty.class);
        for (Object[] row : submissions.countSolvedByDifficulty(clientId, Verdict.ACCEPTED)) {
            solvedBy.put((Difficulty) row[0], (Long) row[1]);
        }

        Map<Difficulty, DifficultyProgress> byDifficulty = new EnumMap<>(Difficulty.class);
        long total = 0;
        long solved = 0;
        for (Difficulty difficulty : Difficulty.values()) {
            long t = totals.getOrDefault(difficulty, 0L);
            long s = solvedBy.getOrDefault(difficulty, 0L);
            byDifficulty.put(difficulty, new DifficultyProgress(t, s));
            total += t;
            solved += s;
        }

        long attempted = submissions.findAttemptedProblemIds(clientId).size();
        return new ProgressSummary(total, solved, attempted, bookmarks.countByClientId(clientId), byDifficulty);
    }
}
