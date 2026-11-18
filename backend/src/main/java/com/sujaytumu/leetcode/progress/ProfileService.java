package com.sujaytumu.leetcode.progress;

import com.sujaytumu.leetcode.discuss.CommentRepository;
import com.sujaytumu.leetcode.discuss.CommentVoteRepository;
import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.social.FollowRepository;
import com.sujaytumu.leetcode.social.ProfileVisitRepository;
import com.sujaytumu.leetcode.solutionpost.SolutionPostRepository;
import com.sujaytumu.leetcode.solutionpost.SolutionPostVoteRepository;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.progress.ProgressService.ProgressSummary;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import com.sujaytumu.leetcode.submission.Verdict;
import java.time.Instant;
import java.time.Duration;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Everything the profile page shows, computed from one client's submission history. */
@Service
public class ProfileService {

    /** Length of the activity calendar, like LeetCode's "past one year". */
    static final int WINDOW_DAYS = 365;

    private static final int RECENT_LIMIT = 15;

    public record DayCount(String date, int count) {}

    public record Badge(
            String id, String title, String description, String category, int target, long progress, boolean earned) {}

    public record RecentSolve(String slug, String title, Difficulty difficulty, String language, Instant at) {}

    public record SkillCount(String tag, long solved) {}

    public record LanguageCount(String language, long solved) {}

    /**
     * Community activity, each with the last 7 days: solutions posted, discussion comments written, and reputation
     * (upvotes received on comments and solutions).
     */
    public record CommunityStats(
            long views,
            long viewsLastWeek,
            long solutions,
            long solutionsLastWeek,
            long discuss,
            long discussLastWeek,
            long reputation,
            long reputationLastWeek) {}

    /** Who follows this profile and whom it follows. */
    public record Social(long followers, long following) {}

    public record ProfileView(
            ProgressSummary progress,
            long attempting,
            long submissionsPastYear,
            int activeDays,
            int maxStreak,
            int currentStreak,
            List<DayCount> calendar,
            List<RecentSolve> recentAccepted,
            List<SkillCount> skills,
            List<LanguageCount> languages,
            List<Badge> badges,
            CommunityStats community,
            Social social) {}

    private final ProgressService progressService;
    private final ProblemRepository problems;
    private final SubmissionRepository submissions;

    private final CommentRepository comments;
    private final CommentVoteRepository commentVotes;
    private final SolutionPostRepository solutionPosts;
    private final SolutionPostVoteRepository solutionVotes;
    private final FollowRepository follows;
    private final ProfileVisitRepository visits;

    public ProfileService(
            ProgressService progressService,
            ProblemRepository problems,
            SubmissionRepository submissions,
            CommentRepository comments,
            CommentVoteRepository commentVotes,
            SolutionPostRepository solutionPosts,
            SolutionPostVoteRepository solutionVotes,
            FollowRepository follows,
            ProfileVisitRepository visits) {
        this.progressService = progressService;
        this.problems = problems;
        this.submissions = submissions;
        this.comments = comments;
        this.commentVotes = commentVotes;
        this.solutionPosts = solutionPosts;
        this.solutionVotes = solutionVotes;
        this.follows = follows;
        this.visits = visits;
    }

    @Transactional(readOnly = true)
    public ProfileView profile(UUID clientId, ZoneId zone) {
        ProgressSummary progress = progressService.summary(clientId);

        LocalDate today = LocalDate.now(zone);
        Instant since = today.minusDays(WINDOW_DAYS - 1L).atStartOfDay(zone).toInstant();
        List<Instant> allTimes = submissions.findSubmissionTimesSince(clientId, Instant.EPOCH);
        List<Instant> times = allTimes.stream().filter(time -> !time.isBefore(since)).toList();
        Map<LocalDate, Integer> perDay = new TreeMap<>();
        Set<LocalDate> activeAllTime = new TreeSet<>();
        for (Instant time : allTimes) {
            LocalDate day = time.atZone(zone).toLocalDate();
            activeAllTime.add(day);
            if (!time.isBefore(since)) {
                perDay.merge(day, 1, Integer::sum);
            }
        }

        List<DayCount> calendar = perDay.entrySet().stream()
                .map(entry -> new DayCount(entry.getKey().toString(), entry.getValue()))
                .toList();

        List<RecentSolve> recent = submissions
                .findRecentWithVerdict(clientId, Verdict.ACCEPTED, PageRequest.of(0, RECENT_LIMIT))
                .stream()
                .map(row -> new RecentSolve(
                        (String) row[1],
                        (String) row[2],
                        (Difficulty) row[3],
                        ((Language) row[4]).name().toLowerCase(),
                        (Instant) row[0]))
                .toList();

        Set<Long> solvedIds = submissions.findProblemIdsWithVerdict(clientId, Verdict.ACCEPTED);
        Map<String, Long> tagCounts = new HashMap<>();
        for (Problem problem : problems.findAllById(solvedIds)) {
            for (String tag : problem.getTags()) {
                tagCounts.merge(tag, 1L, Long::sum);
            }
        }
        List<SkillCount> skills = tagCounts.entrySet().stream()
                .map(entry -> new SkillCount(entry.getKey(), entry.getValue()))
                .sorted(Comparator.comparingLong(SkillCount::solved)
                        .reversed()
                        .thenComparing(SkillCount::tag))
                .toList();

        List<LanguageCount> languages = submissions.countSolvedByLanguage(clientId, Verdict.ACCEPTED).stream()
                .map(row -> new LanguageCount(((Language) row[0]).name().toLowerCase(), (Long) row[1]))
                .sorted(Comparator.comparingLong(LanguageCount::solved)
                        .reversed()
                        .thenComparing(LanguageCount::language))
                .toList();

        return new ProfileView(
                progress,
                Math.max(0, progress.attempted() - progress.solved()),
                times.size(),
                perDay.size(),
                longestRun(perDay.keySet()),
                currentRun(perDay.keySet(), today),
                calendar,
                recent,
                skills,
                languages,
                Badges.compute(
                        progress.solved(),
                        progress.byDifficulty().get(Difficulty.HARD).solved(),
                        activeAllTime.size(),
                        longestRun(activeAllTime)),
                community(clientId),
                new Social(follows.countByFolloweeId(clientId), follows.countByFollowerId(clientId)));
    }

    private CommunityStats community(UUID clientId) {
        Instant weekAgo = Instant.now().minus(Duration.ofDays(7));
        return new CommunityStats(
                visits.countByProfileId(clientId),
                visits.countByProfileIdAndCreatedAtAfter(clientId, weekAgo),
                solutionPosts.countByClientId(clientId),
                solutionPosts.countByClientIdAndCreatedAtAfter(clientId, weekAgo),
                comments.countByClientId(clientId),
                comments.countByClientIdAndCreatedAtAfter(clientId, weekAgo),
                commentVotes.countReceived(clientId) + solutionVotes.countReceived(clientId),
                commentVotes.countReceivedSince(clientId, weekAgo) + solutionVotes.countReceivedSince(clientId, weekAgo));
    }

    /** Longest run of consecutive active days. {@code days} must be sorted ascending. */
    static int longestRun(Iterable<LocalDate> days) {
        int best = 0;
        int run = 0;
        LocalDate previous = null;
        for (LocalDate day : days) {
            run = previous != null && day.equals(previous.plusDays(1)) ? run + 1 : 1;
            best = Math.max(best, run);
            previous = day;
        }
        return best;
    }

    /** Consecutive active days ending today, or yesterday when today has no activity yet. */
    static int currentRun(Set<LocalDate> days, LocalDate today) {
        LocalDate cursor = days.contains(today) ? today : today.minusDays(1);
        int run = 0;
        while (days.contains(cursor)) {
            run++;
            cursor = cursor.minusDays(1);
        }
        return run;
    }
}
