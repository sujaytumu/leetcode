package com.sujaytumu.leetcode.contest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class RatingServiceTest {

    @Test
    void winnerRisesLoserFallsAndNobodyMovesMoreThanTheCap() {
        double[] before = {1500, 1500, 1500, 1500};
        double[] after = RatingService.update(before, new int[] {1, 2, 3, 4}, new int[] {0, 0, 0, 0});
        assertTrue(after[0] > 1500 && after[0] <= 1500 + RatingService.MAX_STEP);
        assertTrue(after[3] < 1500 && after[3] >= 1500 - RatingService.MAX_STEP);
        for (int i = 1; i < after.length; i++) {
            assertTrue(after[i - 1] > after[i], "better rank must end with a higher rating");
        }
    }

    @Test
    void finishingAsExpectedBarelyMovesARatingForAnExperiencedPlayer() {
        double[] before = {1900, 1700, 1500, 1300};
        double[] after = RatingService.update(before, new int[] {1, 2, 3, 4}, new int[] {30, 30, 30, 30});
        for (int i = 0; i < before.length; i++) {
            assertTrue(Math.abs(after[i] - before[i]) < 120, "player " + i + " moved " + (after[i] - before[i]));
        }
    }

    @Test
    void tiedPlayersGetTheSameUpdate() {
        double[] after = RatingService.update(new double[] {1500, 1500, 1500}, new int[] {1, 2, 2}, new int[] {0, 0, 0});
        assertEquals(after[1], after[2], 1e-9);
        assertTrue(after[0] > after[1]);
    }

    @Test
    void expectedRankOfAnEqualFieldIsTheMiddle() {
        // Against 3 equal opponents a player expects 1 + 3 * 0.5 = 2.5.
        assertEquals(2.5, RatingService.expectedRank(1500, 0, new double[] {1500, 1500, 1500, 1500}), 1e-9);
    }
}
