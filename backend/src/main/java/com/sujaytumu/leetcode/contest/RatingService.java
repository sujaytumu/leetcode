package com.sujaytumu.leetcode.contest;

import com.sujaytumu.leetcode.contest.ContestService.Scored;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * LeetCode-style contest ratings, derived from the weekly contests' standings. Everyone starts at 1500. After each
 * finished contest with at least two participants, a player's "performance" is the rating at which they would be
 * expected to finish at their actual rank (against the field's ratings), and the rating moves toward it. Finished
 * contests never change, so each is processed once and kept in memory; a restart replays them from the submissions.
 */
@Service
public class RatingService {

    static final double INITIAL = 1500;
    /** One contest never moves a rating by more than this, so tiny contests cannot cause wild swings. */
    static final double MAX_STEP = 250;
    private static final int HISTORY_SHOWN = 100;
    private static final int BUCKET = 100;

    public record Point(long contest, String title, Instant at, int rating, int rank, int change) {}

    public record Bucket(int from, int count) {}

    public record RatingView(
            Integer rating,
            int attended,
            Integer globalRank,
            int rated,
            Double topPercent,
            Integer peak,
            List<Point> history,
            List<Bucket> distribution) {}

    private static final class State {
        double rating = INITIAL;
        int attended;
        final List<Point> history = new ArrayList<>();
    }

    private final ProblemRepository problems;
    private final SubmissionRepository submissions;
    private final Map<UUID, State> states = new HashMap<>();
    private long processedThrough = -1;

    public RatingService(ProblemRepository problems, SubmissionRepository submissions) {
        this.problems = problems;
        this.submissions = submissions;
    }

    @Transactional(readOnly = true)
    public synchronized RatingView view(UUID clientId, Instant now) {
        advance(now);
        State mine = clientId == null ? null : states.get(clientId);

        TreeMap<Integer, Integer> buckets = new TreeMap<>();
        for (State s : states.values()) {
            buckets.merge((int) Math.floor(s.rating / BUCKET) * BUCKET, 1, Integer::sum);
        }
        List<Bucket> distribution = buckets.entrySet().stream()
                .map(e -> new Bucket(e.getKey(), e.getValue()))
                .toList();

        if (mine == null) {
            return new RatingView(null, 0, null, states.size(), null, null, List.of(), distribution);
        }
        int better = 0;
        for (State s : states.values()) {
            if (Math.round(s.rating) > Math.round(mine.rating)) {
                better++;
            }
        }
        int rank = better + 1;
        double top = Math.round(rank * 10000.0 / states.size()) / 100.0;
        int peak = mine.history.stream().mapToInt(Point::rating).max().orElse((int) Math.round(mine.rating));
        List<Point> history = mine.history.size() <= HISTORY_SHOWN
                ? List.copyOf(mine.history)
                : List.copyOf(mine.history.subList(mine.history.size() - HISTORY_SHOWN, mine.history.size()));
        return new RatingView((int) Math.round(mine.rating), mine.attended, rank, states.size(), top, peak, history, distribution);
    }

    /** Processes every contest that has finished since the last call. */
    private void advance(Instant now) {
        long lastFinished = ContestService.currentIndex(now) - 1;
        if (lastFinished <= processedThrough) {
            return;
        }
        List<Problem> bank = problems.findAll(Sort.by("id"));
        for (long n = processedThrough + 1; n <= lastFinished; n++) {
            applyContest(n, bank);
            processedThrough = n;
        }
    }

    private void applyContest(long n, List<Problem> bank) {
        List<Problem> picked = ContestService.pick(n, bank);
        if (picked.isEmpty()) {
            return;
        }
        List<Long> ids = picked.stream().map(Problem::getId).toList();
        Instant start = ContestService.startOf(n);
        List<Submission> window = submissions.findInWindow(ids, start, start.plus(ContestService.LENGTH));
        List<Scored> ranked = ContestService.score(ids, start, window);
        int size = ranked.size();
        if (size < 2) {
            return;
        }
        int[] rank = new int[size];
        double[] before = new double[size];
        int[] attended = new int[size];
        for (int i = 0; i < size; i++) {
            Scored s = ranked.get(i);
            boolean tied = i > 0
                    && s.score() == ranked.get(i - 1).score()
                    && s.finishSeconds() == ranked.get(i - 1).finishSeconds();
            rank[i] = tied ? rank[i - 1] : i + 1;
            State state = states.get(s.clientId());
            before[i] = state == null ? INITIAL : state.rating;
            attended[i] = state == null ? 0 : state.attended;
        }
        double[] after = update(before, rank, attended);
        Instant end = start.plus(ContestService.LENGTH);
        for (int i = 0; i < size; i++) {
            State state = states.computeIfAbsent(ranked.get(i).clientId(), id -> new State());
            state.rating = after[i];
            state.attended++;
            state.history.add(new Point(
                    n,
                    "Weekly Contest " + (n + 1),
                    end,
                    (int) Math.round(after[i]),
                    rank[i],
                    (int) Math.round(after[i]) - (int) Math.round(before[i])));
        }
    }

    /**
     * One contest's rating update. {@code rank} is 1-based (ties share a rank), {@code attended} is how many
     * contests each player had finished before this one; newcomers move the most.
     */
    static double[] update(double[] ratings, int[] rank, int[] attended) {
        int n = ratings.length;
        double[] out = new double[n];
        for (int i = 0; i < n; i++) {
            double expected = expectedRank(ratings[i], i, ratings);
            double target = Math.sqrt(expected * rank[i]);
            double lo = 0;
            double hi = 4000;
            for (int step = 0; step < 40; step++) {
                double mid = (lo + hi) / 2;
                if (expectedRank(mid, i, ratings) > target) {
                    lo = mid; // expected to finish too low at this rating: performance is higher
                } else {
                    hi = mid;
                }
            }
            double performance = (lo + hi) / 2;
            double weight = 0.4 + 0.6 / (1 + attended[i]);
            double move = Math.max(-MAX_STEP, Math.min(MAX_STEP, (performance - ratings[i]) * weight));
            out[i] = ratings[i] + move;
        }
        return out;
    }

    /** Expected finishing place of a player rated {@code r}: 1 plus how many others are expected to beat them. */
    static double expectedRank(double r, int self, double[] ratings) {
        double sum = 1.0;
        for (int j = 0; j < ratings.length; j++) {
            if (j != self) {
                sum += 1.0 / (1.0 + Math.pow(10, (r - ratings[j]) / 400.0));
            }
        }
        return sum;
    }
}
