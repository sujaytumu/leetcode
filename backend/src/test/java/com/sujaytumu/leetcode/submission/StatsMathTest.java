package com.sujaytumu.leetcode.submission;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sujaytumu.leetcode.submission.SubmissionDtos.Distribution;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class StatsMathTest {

    @Test
    void aloneThereIsNobodyToBeat() {
        Distribution d = StatsMath.distribution(List.of(40), 40);
        assertNull(d.beatsPercent());
        assertEquals(1, d.bins().size());
        assertEquals(1, d.bins().get(0).count());
    }

    @Test
    void withTwoUsersTheFasterOneBeatsTheOtherCompletely() {
        assertEquals(100.0, StatsMath.distribution(List.of(10, 30), 10).beatsPercent());
        assertEquals(0.0, StatsMath.distribution(List.of(10, 30), 30).beatsPercent());
    }

    @Test
    void tiesDoNotCountAsBeaten() {
        // others: 20, 20, 50, 60 -> only 50 and 60 are strictly slower than 20.
        assertEquals(50.0, StatsMath.distribution(List.of(20, 20, 20, 50, 60), 20).beatsPercent());
    }

    @Test
    void percentageIsRoundedToOneDecimalOfTheOthers() {
        // 3 others, 1 slower -> 33.3%.
        assertEquals(33.3, StatsMath.distribution(List.of(5, 5, 5, 9), 5).beatsPercent());
        // 8 of 9 others slower -> 88.9%.
        assertEquals(88.9, StatsMath.distribution(List.of(1, 5, 5, 5, 5, 5, 5, 5, 5, 1), 1).beatsPercent());
    }

    @Test
    void binsCoverEveryMeasurementAndMarkYours() {
        List<Integer> all = List.of(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100);
        Distribution d = StatsMath.distribution(all, 100);
        assertEquals(StatsMath.BINS, d.bins().size());
        assertEquals(all.size(), d.bins().stream().mapToInt(b -> b.count()).sum());
        assertEquals(StatsMath.BINS - 1, d.userBin());
        assertEquals(0, d.bins().get(0).from());
        assertEquals(100, d.bins().get(StatsMath.BINS - 1).to());
    }

    @Test
    void oneBestValuePerOtherUserAndNeverMyOwnOtherTries() {
        UUID me = UUID.randomUUID();
        UUID ann = UUID.randomUUID();
        UUID bob = UUID.randomUUID();
        List<Object[]> rows = List.of(
                new Object[] {1L, 50, 900, ann},
                new Object[] {2L, 30, 800, ann}, // Ann's best
                new Object[] {3L, 70, 700, bob},
                new Object[] {4L, 10, 100, me}, // my other, faster try must not be counted as someone to beat
                new Object[] {5L, null, null, bob});
        List<Integer> runtimes = StatsMath.oneBestPerUser(rows, 1, me, 40);
        assertEquals(3, runtimes.size());
        assertTrue(runtimes.containsAll(List.of(30, 70, 40)));
        // Beats Bob (70) but not Ann (30): 1 of 2 other users.
        assertEquals(50.0, StatsMath.distribution(runtimes, 40).beatsPercent());
    }

    @Test
    void resubmittingTheSameSolutionNeverBeatsYourself() {
        UUID me = UUID.randomUUID();
        List<Object[]> rows = List.of(new Object[] {1L, 40, 100, me}, new Object[] {2L, 40, 100, me});
        List<Integer> runtimes = StatsMath.oneBestPerUser(rows, 1, me, 40);
        assertEquals(List.of(40), runtimes);
        assertNull(StatsMath.distribution(runtimes, 40).beatsPercent());
    }
}
