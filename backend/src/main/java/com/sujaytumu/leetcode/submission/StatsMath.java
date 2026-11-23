package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.submission.SubmissionDtos.Bin;
import com.sujaytumu.leetcode.submission.SubmissionDtos.Distribution;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** Histogram and "beats X%" maths for runtime and memory, kept free of Spring so it can be unit-tested. */
final class StatsMath {

    static final int BINS = 10;

    private StatsMath() {}

    /**
     * @param all every accepted measurement for the problem and language, including {@code mine}
     * @param mine the submission being looked at
     */
    static Distribution distribution(List<Integer> all, int mine) {
        int min = mine, max = mine;
        int worse = 0;
        for (int v : all) {
            min = Math.min(min, v);
            max = Math.max(max, v);
            if (v > mine) {
                worse++;
            }
        }
        // `all` contains the submission itself, which is never strictly worse than itself.
        int others = Math.max(0, all.size() - 1);
        Double beats = others == 0 ? null : Math.round(worse * 1000.0 / others) / 10.0;

        int bins = min == max ? 1 : BINS;
        double width = bins == 1 ? 1 : (max - min) / (double) bins;
        int[] counts = new int[bins];
        for (int v : all) {
            counts[binOf(v, min, width, bins)]++;
        }
        List<Bin> out = new ArrayList<>(bins);
        for (int i = 0; i < bins; i++) {
            int from = bins == 1 ? min : (int) Math.round(min + i * width);
            int to = bins == 1 ? min : (i == bins - 1 ? max : (int) Math.round(min + (i + 1) * width));
            out.add(new Bin(from, to, counts[i]));
        }
        return new Distribution(mine, beats, binOf(mine, min, width, bins), out);
    }

    /**
     * The measurements to compare a submission with: the best (smallest) value of every <em>other</em> user, plus the
     * submission itself. One value per user keeps "beats X%" about people, so a user re-submitting the same
     * solution never beats their own earlier tries.
     *
     * @param rows   [id, runtimeMs, memoryKb, clientId] of accepted submissions
     * @param column 1 for runtime, 2 for memory
     * @param me     the client who owns the submission
     * @param mine   the submission's own value
     */
    static List<Integer> oneBestPerUser(List<Object[]> rows, int column, UUID me, int mine) {
        Map<UUID, Integer> best = new HashMap<>();
        for (Object[] row : rows) {
            if (row[column] == null || me.equals(row[3])) {
                continue;
            }
            best.merge((UUID) row[3], ((Number) row[column]).intValue(), Math::min);
        }
        List<Integer> all = new ArrayList<>(best.values());
        all.add(mine);
        return all;
    }

    private static int binOf(int value, int min, double width, int bins) {
        if (bins == 1) {
            return 0;
        }
        return Math.min(bins - 1, (int) ((value - min) / width));
    }
}
