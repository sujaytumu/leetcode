package com.sujaytumu.leetcode.common;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException;
import com.sujaytumu.leetcode.config.AppProperties;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class RunRateLimiterTest {

    private static RunRateLimiter limiter(int perMinute) {
        AppProperties props = new AppProperties(
                new AppProperties.Cors(List.of()),
                new AppProperties.Seed(false),
                new AppProperties.RateLimit(perMinute),
                new AppProperties.Judge0("", "", 2.0, 20),
                new AppProperties.Auth("", 30, 8));
        return new RunRateLimiter(props);
    }

    @Test
    void blocksAfterLimitWithinWindow() {
        RunRateLimiter limiter = limiter(3);
        UUID client = UUID.randomUUID();
        for (int i = 0; i < 3; i++) {
            assertDoesNotThrow(() -> limiter.check(client));
        }
        assertThrows(TooManyRequestsException.class, () -> limiter.check(client));
    }

    @Test
    void limitsAreTrackedPerClient() {
        RunRateLimiter limiter = limiter(1);
        UUID a = UUID.randomUUID();
        UUID b = UUID.randomUUID();
        limiter.check(a);
        assertDoesNotThrow(() -> limiter.check(b));
        assertThrows(TooManyRequestsException.class, () -> limiter.check(a));
    }
}
