package com.sujaytumu.leetcode;

import com.sujaytumu.leetcode.judge.CodeExecutor;
import com.sujaytumu.leetcode.judge.Language;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;

/**
 * Replaces the real sandbox with a deterministic fake. The submitted "code" is a marker that selects
 * behaviour, which lets tests cover every verdict without running untrusted code.
 */
@TestConfiguration
public class TestExecutorConfig {

    public static final String SOLVE_TWO_SUM = "SOLVE_TWO_SUM";
    public static final String WRONG_ANSWER = "WRONG_ANSWER";
    public static final String COMPILE_ERROR = "COMPILE_ERROR";
    public static final String RUNTIME_ERROR = "RUNTIME_ERROR";
    public static final String TIME_LIMIT = "TIME_LIMIT";

    @Bean
    @Primary
    public CodeExecutor fakeCodeExecutor() {
        return new CodeExecutor() {
            @Override
            public ExecutionResult execute(Language language, String sourceCode, String stdin) {
                if (sourceCode.contains(COMPILE_ERROR)) {
                    return new ExecutionResult(Status.COMPILE_ERROR, "", "", "error: ';' expected", null);
                }
                if (sourceCode.contains(RUNTIME_ERROR)) {
                    return new ExecutionResult(Status.RUNTIME_ERROR, "", "IndexError: list index out of range", "", 0.01);
                }
                if (sourceCode.contains(TIME_LIMIT)) {
                    return new ExecutionResult(Status.TIME_LIMIT_EXCEEDED, "", "", "", 2.0);
                }
                if (sourceCode.contains(WRONG_ANSWER)) {
                    return ExecutionResult.ok("9 9\n", 0.01);
                }
                if (sourceCode.contains(SOLVE_TWO_SUM)) {
                    return ExecutionResult.ok(twoSum(stdin), 0.02);
                }
                return ExecutionResult.ok("", 0.01);
            }
        };
    }

    /** Reads the two-sum input format (n, nums, target) and prints the answer indices. */
    static String twoSum(String stdin) {
        String[] lines = stdin.split("\n");
        String[] tokens = lines[1].trim().split("\\s+");
        int target = Integer.parseInt(lines[2].trim());
        for (int i = 0; i < tokens.length; i++) {
            for (int j = i + 1; j < tokens.length; j++) {
                if (Integer.parseInt(tokens[i]) + Integer.parseInt(tokens[j]) == target) {
                    return i + " " + j + "\n";
                }
            }
        }
        return "-1 -1\n";
    }
}
