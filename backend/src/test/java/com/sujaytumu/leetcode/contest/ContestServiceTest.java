package com.sujaytumu.leetcode.contest;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.Verdict;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

class ContestServiceTest {

    private static final Instant START = ContestService.ANCHOR;

    private static Submission sub(UUID client, long problem, Verdict verdict, long minutesIn) {
        Submission s = new Submission(client, problem, Language.PYTHON, "x", verdict, 0, 1, 10);
        ReflectionTestUtils.setField(s, "createdAt", START.plus(Duration.ofMinutes(minutesIn)));
        return s;
    }

    private static Problem problem(long id, Difficulty d) {
        Problem p = new Problem("p" + id, "Problem " + id, d, "d");
        ReflectionTestUtils.setField(p, "id", id);
        return p;
    }

    @Test
    void scheduleRunsEverySundayForNinetyMinutes() {
        assertEquals(0, ContestService.currentIndex(START));
        assertEquals("RUNNING", ContestService.stateOf(0, START.plusSeconds(5399)));
        assertEquals("FINISHED", ContestService.stateOf(0, START.plusSeconds(5400)));
        assertEquals(1, ContestService.currentIndex(START.plus(Duration.ofMinutes(91)))); // next one is upcoming
        assertEquals("UPCOMING", ContestService.stateOf(1, START.plus(Duration.ofMinutes(91))));
        assertEquals(START.plus(Duration.ofDays(14)), ContestService.startOf(2));
        assertEquals(0, ContestService.currentIndex(START.minus(Duration.ofDays(30)))); // before the first contest
    }

    @Test
    void pickIsDeterministicAndFollowsEasyMediumMediumHard() {
        List<Problem> bank = new ArrayList<>();
        for (long i = 1; i <= 12; i++) {
            bank.add(problem(i, i <= 3 ? Difficulty.EASY : i <= 9 ? Difficulty.MEDIUM : Difficulty.HARD));
        }
        List<Problem> first = ContestService.pick(7, bank);
        assertEquals(first, ContestService.pick(7, bank));
        assertEquals(
                List.of(Difficulty.EASY, Difficulty.MEDIUM, Difficulty.MEDIUM, Difficulty.HARD),
                first.stream().map(Problem::getDifficulty).toList());
        assertEquals(4, first.stream().distinct().count());
        assertTrue(ContestService.pick(8, bank) != null);
    }

    private static Problem tagged(long id, Difficulty d, String... tags) {
        Problem p = problem(id, d);
        p.getTags().addAll(List.of(tags));
        return p;
    }

    @Test
    void laterContestsFollowLeetCodeStyleTopics() {
        List<Problem> bank = new ArrayList<>();
        bank.add(tagged(1, Difficulty.EASY, "array"));
        bank.add(tagged(2, Difficulty.EASY, "tree"));
        bank.add(tagged(3, Difficulty.MEDIUM, "string"));
        bank.add(tagged(4, Difficulty.MEDIUM, "dynamic-programming"));
        bank.add(tagged(5, Difficulty.MEDIUM, "binary-search"));
        bank.add(tagged(6, Difficulty.MEDIUM, "tree"));
        bank.add(tagged(7, Difficulty.MEDIUM, "graph"));
        bank.add(tagged(8, Difficulty.HARD, "dynamic-programming"));
        bank.add(tagged(9, Difficulty.HARD, "graph"));
        for (long n = ContestService.THEMED_FROM; n < ContestService.THEMED_FROM + 12; n++) {
            List<Problem> q = ContestService.pick(n, bank);
            assertEquals(q, ContestService.pick(n, bank));
            assertEquals(4, q.size());
            assertEquals(1L, q.get(0).getId()); // the only easy on a q1 topic
            assertEquals(n % 2 == 0 ? 8L : 9L, q.get(3).getId()); // hard: dp on even weeks, graph on odd
            assertTrue(q.get(1).getTags().stream().anyMatch(t -> t.equals("string")));
            assertEquals(4, q.stream().distinct().count());
        }
    }

    @Test
    void scoringUsesPointsPenaltiesAndFinishTime() {
        UUID a = UUID.randomUUID();
        UUID b = UUID.randomUUID();
        UUID c = UUID.randomUUID();
        List<Long> ids = List.of(10L, 20L, 30L, 40L);
        List<Submission> window = List.of(
                // a: two wrong answers and a compile error (free) before accepting problem 10 at minute 10
                sub(a, 10, Verdict.WRONG_ANSWER, 2), sub(a, 10, Verdict.COMPILE_ERROR, 3),
                sub(a, 10, Verdict.WRONG_ANSWER, 5), sub(a, 10, Verdict.ACCEPTED, 10),
                // b: problem 10 at minute 5 and the hard one at minute 60; a later wrong answer is ignored
                sub(b, 10, Verdict.ACCEPTED, 5), sub(b, 40, Verdict.ACCEPTED, 60), sub(b, 10, Verdict.WRONG_ANSWER, 70),
                // c: only wrong answers
                sub(c, 20, Verdict.WRONG_ANSWER, 4));

        List<ContestService.Scored> ranked = ContestService.score(ids, START, window);

        assertEquals(List.of(b, a, c), ranked.stream().map(ContestService.Scored::clientId).toList());
        assertEquals(3 + 6, ranked.get(0).score());
        assertEquals(60 * 60, ranked.get(0).finishSeconds());
        assertEquals(List.of(true, false, false, true), ranked.get(0).solved());
        assertEquals(3, ranked.get(1).score());
        assertEquals(10 * 60 + 2 * 300, ranked.get(1).finishSeconds()); // 10 min + two 5-minute penalties
        assertEquals(0, ranked.get(2).score());
    }

    @Test
    void equalScoresAreBrokenByFinishTime() {
        UUID fast = UUID.randomUUID();
        UUID slow = UUID.randomUUID();
        List<ContestService.Scored> ranked = ContestService.score(List.of(1L), START, List.of(
                sub(slow, 1, Verdict.ACCEPTED, 30), sub(fast, 1, Verdict.ACCEPTED, 12)));
        assertEquals(fast, ranked.get(0).clientId());
    }
}
