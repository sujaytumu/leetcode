package com.sujaytumu.leetcode.judge;

/** Runs untrusted source code in an isolated sandbox. Implementations must never run code in-process. */
public interface CodeExecutor {

    ExecutionResult execute(Language language, String sourceCode, String stdin);

    enum Status {
        OK,
        COMPILE_ERROR,
        RUNTIME_ERROR,
        TIME_LIMIT_EXCEEDED,
        INTERNAL_ERROR
    }

    record ExecutionResult(Status status, String stdout, String stderr, String compileOutput, Double timeSeconds) {

        public static ExecutionResult ok(String stdout, Double timeSeconds) {
            return new ExecutionResult(Status.OK, stdout, "", "", timeSeconds);
        }
    }
}
