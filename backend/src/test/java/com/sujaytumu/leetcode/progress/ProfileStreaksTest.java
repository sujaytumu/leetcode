package com.sujaytumu.leetcode.progress;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.time.LocalDate;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import org.junit.jupiter.api.Test;

class ProfileStreaksTest {

    private static final List<LocalDate> DAYS = List.of(
            LocalDate.of(2026, 11, 1),
            LocalDate.of(2026, 11, 2),
            LocalDate.of(2026, 11, 3),
            LocalDate.of(2026, 11, 10),
            LocalDate.of(2026, 11, 16),
            LocalDate.of(2026, 11, 17));

    @Test
    void longestRunFindsTheBestConsecutiveStretch() {
        assertEquals(3, ProfileService.longestRun(DAYS));
        assertEquals(0, ProfileService.longestRun(List.of()));
    }

    @Test
    void currentRunCountsBackFromTodayOrYesterday() {
        Set<LocalDate> days = new TreeSet<>(DAYS);
        assertEquals(2, ProfileService.currentRun(days, LocalDate.of(2026, 11, 17)));
        // nothing yet today: yesterday's streak is still alive
        assertEquals(2, ProfileService.currentRun(days, LocalDate.of(2026, 11, 18)));
        // a full day missed: streak is broken
        assertEquals(0, ProfileService.currentRun(days, LocalDate.of(2026, 11, 19)));
    }
}
