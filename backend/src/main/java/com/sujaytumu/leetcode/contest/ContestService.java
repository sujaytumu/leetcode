package com.sujaytumu.leetcode.contest;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.profileinfo.ProfileInfo;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoRepository;
import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import com.sujaytumu.leetcode.submission.Verdict;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * A weekly contest needs no stored state. Contest {@code n} starts every seventh day at 02:30 UTC (08:00 IST) and
 * lasts 90 minutes. Its four problems (Easy, Medium, Medium, Hard, worth 3, 4, 5 and 6 points) are picked
 * deterministically from {@code n}, and the standings are computed from the submissions made in that window.
 * Each wrong submission before the accepted one adds a 5 minute penalty; compile and judge errors are free.
 */
@Service
public class ContestService {

    static final Instant ANCHOR = Instant.parse("2024-01-07T02:30:00Z"); // a Sunday: contest 0
    static final Duration WEEK = Duration.ofDays(7);
    static final Duration LENGTH = Duration.ofMinutes(90);
    static final long PENALTY_SECONDS = 5 * 60;
    static final int[] POINTS = {3, 4, 5, 6};
    static final int MAX_ROWS = 50;
    public static final int PAST_SHOWN = 8;

    public record ContestProblem(String slug, String title, Difficulty difficulty, int points) {}

    /** {@code problems} is null until the contest starts, so the questions stay hidden. */
    public record ContestView(
            long id, String title, Instant start, Instant end, String state, List<ContestProblem> problems) {}

    public record Row(int rank, String name, int score, long finishSeconds, List<Boolean> solved, boolean you) {}

    public record Standings(ContestView contest, int participants, List<Row> rows, Row me) {}

    public record Overview(Instant now, ContestView current, List<ContestView> past) {}

    private final ProblemRepository problems;
    private final SubmissionRepository submissions;
    private final ProfileInfoRepository profiles;

    public ContestService(ProblemRepository problems, SubmissionRepository submissions, ProfileInfoRepository profiles) {
        this.problems = problems;
        this.submissions = submissions;
        this.profiles = profiles;
    }

    // ------------------------------------------------------------------ schedule (pure)

    static Instant startOf(long n) {
        return ANCHOR.plus(WEEK.multipliedBy(n));
    }

    /** The contest that is running now, otherwise the next one to start. */
    static long currentIndex(Instant now) {
        long weeks = Duration.between(ANCHOR, now).toSeconds() / WEEK.toSeconds();
        if (now.isBefore(ANCHOR)) {
            return 0;
        }
        return now.isBefore(startOf(weeks).plus(LENGTH)) ? weeks : weeks + 1;
    }

    static String stateOf(long n, Instant now) {
        if (now.isBefore(startOf(n))) {
            return "UPCOMING";
        }
        return now.isBefore(startOf(n).plus(LENGTH)) ? "RUNNING" : "FINISHED";
    }

    /** Easy, Medium, Medium, Hard chosen deterministically from the contest number (fewer if the bank is small). */
    static List<Problem> pick(long n, List<Problem> bank) {
        Random rnd = new Random(n * 1_000_003L + 17);
        Map<Difficulty, List<Problem>> byDifficulty = bank.stream()
                .sorted(Comparator.comparing(Problem::getId))
                .collect(Collectors.groupingBy(Problem::getDifficulty));
        List<Problem> out = new ArrayList<>();
        for (Difficulty d : new Difficulty[] {Difficulty.EASY, Difficulty.MEDIUM, Difficulty.MEDIUM, Difficulty.HARD}) {
            List<Problem> pool = new ArrayList<>(byDifficulty.getOrDefault(d, List.of()));
            pool.removeAll(out);
            if (!pool.isEmpty()) {
                out.add(pool.get(rnd.nextInt(pool.size())));
            }
        }
        return out;
    }

    // ------------------------------------------------------------------ scoring (pure)

    record Scored(UUID clientId, int score, long finishSeconds, List<Boolean> solved) {}

    /**
     * @param problemIds the contest problems in order (index = points slot)
     * @param window submissions inside the contest window, any order
     */
    static List<Scored> score(List<Long> problemIds, Instant start, Collection<Submission> window) {
        Map<UUID, Map<Long, List<Submission>>> byClient = new HashMap<>();
        for (Submission s : window) {
            byClient.computeIfAbsent(s.getClientId(), k -> new HashMap<>())
                    .computeIfAbsent(s.getProblemId(), k -> new ArrayList<>()).add(s);
        }
        List<Scored> out = new ArrayList<>();
        for (Map.Entry<UUID, Map<Long, List<Submission>>> client : byClient.entrySet()) {
            int score = 0;
            long lastAccepted = 0;
            long penalties = 0;
            List<Boolean> solved = new ArrayList<>();
            for (int i = 0; i < problemIds.size(); i++) {
                List<Submission> subs = new ArrayList<>(client.getValue().getOrDefault(problemIds.get(i), List.of()));
                subs.sort(Comparator.comparing(Submission::getCreatedAt));
                long wrong = 0;
                Submission accepted = null;
                for (Submission s : subs) {
                    if (s.getVerdict() == Verdict.ACCEPTED) {
                        accepted = s;
                        break;
                    }
                    if (s.getVerdict() != Verdict.COMPILE_ERROR && s.getVerdict() != Verdict.INTERNAL_ERROR) {
                        wrong++;
                    }
                }
                solved.add(accepted != null);
                if (accepted != null) {
                    score += POINTS[Math.min(i, POINTS.length - 1)];
                    lastAccepted = Math.max(lastAccepted, Duration.between(start, accepted.getCreatedAt()).toSeconds());
                    penalties += wrong;
                }
            }
            out.add(new Scored(client.getKey(), score, lastAccepted + penalties * PENALTY_SECONDS, solved));
        }
        out.sort(Comparator.comparingInt(Scored::score).reversed()
                .thenComparingLong(Scored::finishSeconds)
                .thenComparing(s -> s.clientId().toString()));
        return out;
    }

    // ------------------------------------------------------------------ queries

    @Transactional(readOnly = true)
    public Overview overview(Instant now) {
        List<Problem> bank = problems.findAll(Sort.by("id"));
        long cur = currentIndex(now);
        List<ContestView> past = new ArrayList<>();
        for (long n = cur - 1; n >= 0 && past.size() < PAST_SHOWN; n--) {
            if (stateOf(n, now).equals("FINISHED")) {
                past.add(view(n, now, bank));
            }
        }
        return new Overview(now, view(cur, now, bank), past);
    }

    @Transactional(readOnly = true)
    public Standings standings(long n, UUID clientId, Instant now) {
        if (n < 0 || n > currentIndex(now)) {
            throw new NotFoundException("Contest not found: " + n);
        }
        List<Problem> bank = problems.findAll(Sort.by("id"));
        ContestView contest = view(n, now, bank);
        if (contest.problems() == null) {
            return new Standings(contest, 0, List.of(), null); // not started: nothing to rank
        }
        List<Problem> picked = pick(n, bank);
        List<Long> ids = picked.stream().map(Problem::getId).toList();
        Instant start = startOf(n);
        List<Submission> window = ids.isEmpty() ? List.of() : submissions.findInWindow(ids, start, start.plus(LENGTH));
        List<Scored> ranked = score(ids, start, window);

        List<Scored> scoring = ranked.stream().filter(s -> s.score() > 0).toList();
        Map<UUID, ProfileInfo> info = profiles
                .findAllById(scoring.stream().limit(MAX_ROWS).map(Scored::clientId).toList()).stream()
                .collect(Collectors.toMap(ProfileInfo::getClientId, Function.identity()));
        List<Row> rows = new ArrayList<>();
        Row me = null;
        for (int i = 0; i < scoring.size(); i++) {
            Scored s = scoring.get(i);
            boolean isMe = s.clientId().equals(clientId);
            if (i >= MAX_ROWS && !isMe) {
                continue;
            }
            ProfileInfo p = info.get(s.clientId());
            if (p == null && isMe) {
                p = profiles.findById(s.clientId()).orElse(null);
            }
            Row row = new Row(i + 1, name(s.clientId(), p), s.score(), s.finishSeconds(), s.solved(), isMe);
            if (isMe) {
                me = row;
            }
            if (i < MAX_ROWS) {
                rows.add(row);
            }
        }
        return new Standings(contest, ranked.size(), rows, me);
    }

    private ContestView view(long n, Instant now, List<Problem> bank) {
        Instant start = startOf(n);
        String state = stateOf(n, now);
        List<ContestProblem> list = null;
        if (!state.equals("UPCOMING")) {
            List<Problem> picked = pick(n, bank);
            list = new ArrayList<>();
            for (int i = 0; i < picked.size(); i++) {
                Problem p = picked.get(i);
                list.add(new ContestProblem(p.getSlug(), p.getTitle(), p.getDifficulty(), POINTS[Math.min(i, POINTS.length - 1)]));
            }
        }
        return new ContestView(n, "Weekly Contest " + (n + 1), start, start.plus(LENGTH), state, list);
    }

    private static String name(UUID id, ProfileInfo p) {
        String n = p == null ? "" : (!p.getUsername().isBlank() ? p.getUsername() : p.getDisplayName());
        return n == null || n.isBlank() ? "user-" + id.toString().substring(0, 4) : n;
    }
}
