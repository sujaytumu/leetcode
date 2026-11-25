package com.sujaytumu.leetcode.judge;

import com.sujaytumu.leetcode.common.ApiExceptions.ExecutionUnavailableException;

/**
 * Tries the primary executor (a Judge0 instance) and, when it is rate limited, busy or unreachable, runs the code on
 * the built-in local runner instead, so a flaky free Judge0 never leaves Run and Submit dead.
 */
public class FallbackCodeExecutor implements CodeExecutor {

    private final CodeExecutor primary;
    private final CodeExecutor fallback;
    /** After the primary fails, skip it for a while so every test case of a submission does not wait on its retries. */
    private static final long COOLDOWN_MILLIS = 60_000;
    private volatile long primaryDownUntil;

    public FallbackCodeExecutor(CodeExecutor primary, CodeExecutor fallback) {
        this.primary = primary;
        this.fallback = fallback;
    }

    @Override
    public ExecutionResult execute(Language language, String sourceCode, String stdin) {
        if (System.currentTimeMillis() < primaryDownUntil) {
            return fallback.execute(language, sourceCode, stdin);
        }
        try {
            return primary.execute(language, sourceCode, stdin);
        } catch (ExecutionUnavailableException primaryDown) {
            primaryDownUntil = System.currentTimeMillis() + COOLDOWN_MILLIS;
            try {
                return fallback.execute(language, sourceCode, stdin);
            } catch (ExecutionUnavailableException fallbackDown) {
                fallbackDown.addSuppressed(primaryDown);
                throw primaryDown; // the primary's message (e.g. "rate limited, try again") is the more useful one
            }
        }
    }

    @Override
    public Health health() {
        if (System.currentTimeMillis() < primaryDownUntil) {
            Health backup = fallback.health();
            if (backup.reachable()) {
                return backup;
            }
        }
        Health first = primary.health();
        if (first.reachable()) {
            return first;
        }
        Health second = fallback.health();
        return second.reachable() ? second : first;
    }
}
