package com.sujaytumu.leetcode.common;

/** Domain exceptions mapped to HTTP statuses by {@link ApiExceptionHandler}. */
public final class ApiExceptions {

    private ApiExceptions() {}

    public static class NotFoundException extends RuntimeException {
        public NotFoundException(String message) {
            super(message);
        }
    }

    public static class ConflictException extends RuntimeException {
        public ConflictException(String message) {
            super(message);
        }
    }

    public static class UnauthorizedException extends RuntimeException {
        public UnauthorizedException(String message) {
            super(message);
        }
    }

    public static class TooManyRequestsException extends RuntimeException {
        public TooManyRequestsException(String message) {
            super(message);
        }
    }

    public static class ExecutionUnavailableException extends RuntimeException {
        public ExecutionUnavailableException(String message) {
            super(message);
        }

        public ExecutionUnavailableException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
