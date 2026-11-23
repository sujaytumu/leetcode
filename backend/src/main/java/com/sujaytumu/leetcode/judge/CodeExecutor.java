package com.sujaytumu.leetcode.judge;

/** Runs untrusted source code in an isolated sandbox. Implementations must never run code in-process. */
public interface CodeExecutor {

    ExecutionResult execute(Language language, String sourceCode, String stdin);

    /** Reports whether code execution is configured and reachable, so the UI can say so up front. */
    default Health health() {
        return new Health(true, true, "custom", "Code execution is available.");
    }

    record Health(boolean enabled, boolean reachable, String provider, String message) {}

    enum Status {
        OK,
        COMPILE_ERROR,
        RUNTIME_ERROR,
        TIME_LIMIT_EXCEEDED,
        INTERNAL_ERROR
    }

    record ExecutionResult(
            Status status, String stdout, String stderr, String compileOutput, Double timeSeconds, Integer memoryKb) {

        /** Result without a memory reading (executors that cannot measure it). */
        public ExecutionResult(Status status, String stdout, String stderr, String compileOutput, Double timeSeconds) {
            this(status, stdout, stderr, compileOutput, timeSeconds, null);
        }

        public static ExecutionResult ok(String stdout, Double timeSeconds) {
            return new ExecutionResult(Status.OK, stdout, "", "", timeSeconds);
        }
    }
}
