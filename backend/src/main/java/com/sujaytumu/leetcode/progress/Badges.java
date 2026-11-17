package com.sujaytumu.leetcode.progress;

import com.sujaytumu.leetcode.progress.ProfileService.Badge;
import java.util.ArrayList;
import java.util.List;

/** Milestone badges, like LeetCode's streak and solved badges. Pure rules so they are trivial to test. */
final class Badges {

    private static final int[] SOLVED = {1, 10, 25, 50, 100};
    private static final int[] HARD = {1, 5};
    private static final int[] STREAK = {3, 7, 30, 100};
    private static final int[] ACTIVE = {10, 30, 50, 100};

    private Badges() {}

    /**
     * @param solved problems solved overall
     * @param hardSolved hard problems solved
     * @param activeDays distinct days with at least one submission, all time
     * @param longestStreak longest run of consecutive active days, all time
     */
    static List<Badge> compute(long solved, long hardSolved, int activeDays, int longestStreak) {
        List<Badge> badges = new ArrayList<>();
        for (int target : SOLVED) {
            String title = target == 1 ? "First Solve" : target + " Problems Solved";
            badges.add(badge("solved-" + target, title, "Solve " + target + (target == 1 ? " problem" : " problems"),
                    "SOLVED", target, solved));
        }
        for (int target : HARD) {
            String title = target == 1 ? "First Hard" : target + " Hards Conquered";
            badges.add(badge("hard-" + target, title, "Solve " + target + " hard " + (target == 1 ? "problem" : "problems"),
                    "HARD", target, hardSolved));
        }
        for (int target : STREAK) {
            badges.add(badge("streak-" + target, target + "-Day Streak",
                    "Submit on " + target + " days in a row", "STREAK", target, longestStreak));
        }
        for (int target : ACTIVE) {
            badges.add(badge("active-" + target, target + " Active Days",
                    "Be active on " + target + " different days", "ACTIVE", target, activeDays));
        }
        return badges;
    }

    private static Badge badge(String id, String title, String description, String category, int target, long value) {
        return new Badge(id, title, description, category, target, Math.min(value, target), value >= target);
    }
}
