package com.sujaytumu.leetcode.leaderboard;

import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.profileinfo.ProfileInfo;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoRepository;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import com.sujaytumu.leetcode.submission.Verdict;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Ranks everyone who has solved at least one problem. Points: Easy 10, Medium 20, Hard 40. */
@Service
public class LeaderboardService {

    public static final int MAX_LIMIT = 100;

    public record Entry(int rank, String name, int easy, int medium, int hard, int solved, int points, boolean you) {}

    public record Board(List<Entry> top, Entry me, int participants) {}

    private final SubmissionRepository submissions;
    private final ProfileInfoRepository profiles;

    public LeaderboardService(SubmissionRepository submissions, ProfileInfoRepository profiles) {
        this.submissions = submissions;
        this.profiles = profiles;
    }

    static int points(int easy, int medium, int hard) {
        return easy * 10 + medium * 20 + hard * 40;
    }

    /** {@code me} is the caller's entry (with their true rank) even when they are outside the top {@code limit}. */
    @Transactional(readOnly = true)
    public Board board(UUID clientId, int limit) {
        int cap = Math.max(1, Math.min(limit, MAX_LIMIT));
        Map<UUID, int[]> counts = new HashMap<>(); // [easy, medium, hard]
        for (Object[] row : submissions.solvedByClientAndDifficulty(Verdict.ACCEPTED)) {
            int[] c = counts.computeIfAbsent((UUID) row[0], k -> new int[3]);
            int n = ((Number) row[2]).intValue();
            switch ((Difficulty) row[1]) {
                case EASY -> c[0] += n;
                case MEDIUM -> c[1] += n;
                case HARD -> c[2] += n;
            }
        }

        List<Map.Entry<UUID, int[]>> ordered = new ArrayList<>(counts.entrySet());
        ordered.sort(Comparator
                .comparingInt((Map.Entry<UUID, int[]> e) -> points(e.getValue()[0], e.getValue()[1], e.getValue()[2])).reversed()
                .thenComparing(Comparator.comparingInt((Map.Entry<UUID, int[]> e) -> e.getValue()[0] + e.getValue()[1] + e.getValue()[2]).reversed())
                .thenComparing(e -> e.getKey().toString()));

        List<UUID> shown = new ArrayList<>(ordered.stream().limit(cap).map(Map.Entry::getKey).toList());
        if (clientId != null && counts.containsKey(clientId) && !shown.contains(clientId)) {
            shown.add(clientId);
        }
        Map<UUID, ProfileInfo> info = profiles.findAllById(shown).stream()
                .collect(Collectors.toMap(ProfileInfo::getClientId, Function.identity()));

        List<Entry> top = new ArrayList<>();
        Entry me = null;
        for (int i = 0; i < ordered.size() && (i < cap || me == null); i++) {
            Map.Entry<UUID, int[]> e = ordered.get(i);
            boolean isMe = e.getKey().equals(clientId);
            if (i >= cap && !isMe) {
                continue;
            }
            int[] c = e.getValue();
            Entry entry = new Entry(i + 1, name(e.getKey(), info.get(e.getKey())), c[0], c[1], c[2], c[0] + c[1] + c[2],
                    points(c[0], c[1], c[2]), isMe);
            if (isMe) {
                me = entry;
            }
            if (i < cap) {
                top.add(entry);
            }
        }
        return new Board(top, me, ordered.size());
    }

    private static String name(UUID id, ProfileInfo p) {
        String n = p == null ? "" : (!p.getUsername().isBlank() ? p.getUsername() : p.getDisplayName());
        return n == null || n.isBlank() ? "user-" + id.toString().substring(0, 4) : n;
    }
}
