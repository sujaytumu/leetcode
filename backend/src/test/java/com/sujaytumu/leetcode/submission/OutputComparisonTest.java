package com.sujaytumu.leetcode.submission;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class OutputComparisonTest {

    @Test
    void ignoresTrailingWhitespaceAndLineEndingStyle() {
        assertTrue(SubmissionService.outputsMatch("0 1\r\n", "0 1\n"));
        assertTrue(SubmissionService.outputsMatch("0 1   \n\n\n", "0 1"));
        assertTrue(SubmissionService.outputsMatch("1 2  \n3 4\t\n", "1 2\n3 4\n"));
    }

    @Test
    void treatsNullAsEmpty() {
        assertTrue(SubmissionService.outputsMatch(null, ""));
        assertTrue(SubmissionService.outputsMatch("", "\n"));
    }

    @Test
    void isStrictAboutContentAndInnerWhitespace() {
        assertFalse(SubmissionService.outputsMatch("0 1", "0  1"));
        assertFalse(SubmissionService.outputsMatch("0 1", "1 0"));
        assertFalse(SubmissionService.outputsMatch("true", "True"));
        assertFalse(SubmissionService.outputsMatch("1\n2", "1\n\n2"));
        assertEquals(false, SubmissionService.outputsMatch("", "0"));
    }

    @Test
    void userPrintsBeforeTheMarkerDoNotChangeTheAnswer() {
        String out = "debug 1\nx=5" + SubmissionService.ANSWER_MARKER + "0 1\n";
        assertEquals("0 1\n", SubmissionService.answerOf(out));
        assertEquals("debug 1\nx=5", SubmissionService.userStdout(out));
        assertTrue(SubmissionService.outputsMatch(SubmissionService.answerOf(out), "0 1\n"));
    }

    @Test
    void outputWithoutAMarkerIsAllAnswer() {
        assertEquals("0 1\n", SubmissionService.answerOf("0 1\n"));
        assertEquals("", SubmissionService.userStdout("0 1\n"));
        assertEquals("", SubmissionService.answerOf(null));
        assertEquals("", SubmissionService.userStdout(null));
    }

    @Test
    void anAnswerPrintedAsNothingStillCompares() {
        String out = "only debug" + SubmissionService.ANSWER_MARKER;
        assertEquals("", SubmissionService.answerOf(out));
        assertEquals("only debug", SubmissionService.userStdout(out));
    }
}
