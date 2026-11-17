package com.sujaytumu.leetcode.progress;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sujaytumu.leetcode.progress.ProfileService.Badge;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class BadgesTest {

    private static Set<String> earned(List<Badge> badges) {
        return badges.stream().filter(Badge::earned).map(Badge::id).collect(Collectors.toSet());
    }

    @Test
    void nothingIsEarnedWithoutActivity() {
        List<Badge> badges = Badges.compute(0, 0, 0, 0);
        assertEquals(15, badges.size());
        assertTrue(earned(badges).isEmpty());
    }

    @Test
    void earnsEveryMilestoneReached() {
        assertEquals(
                Set.of("solved-1", "solved-10", "hard-1", "streak-3", "streak-7", "active-10", "active-30"),
                earned(Badges.compute(10, 1, 31, 8)));
    }

    @Test
    void progressIsCappedAtTheTarget() {
        Badge notYet = Badges.compute(10, 0, 0, 0).stream().filter(b -> b.id().equals("solved-25")).findFirst().orElseThrow();
        assertEquals(10, notYet.progress());
        assertEquals(25, notYet.target());
        Badge done = Badges.compute(500, 0, 0, 0).stream().filter(b -> b.id().equals("solved-100")).findFirst().orElseThrow();
        assertEquals(100, done.progress());
    }
}
