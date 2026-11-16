package com.sujaytumu.leetcode.judge;

import com.sujaytumu.leetcode.common.ApiExceptions.ExecutionUnavailableException;

/** Used when no sandbox is configured. Refuses to execute anything. */
public class DisabledCodeExecutor implements CodeExecutor {

    @Override
    public ExecutionResult execute(Language language, String sourceCode, String stdin) {
        throw new ExecutionUnavailableException(
                "Code execution is not configured on this server. Set JUDGE0_URL to a Judge0 instance.");
    }

    @Override
    public Health health() {
        return new Health(false, false, "none", "Code execution is not configured on this server.");
    }
}
