package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException;
import com.sujaytumu.leetcode.config.AppProperties;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/** Blocks password guessing: too many failures per key (username or IP) within the window locks that key out. */
@Component
public class LoginThrottle {

    private static final long WINDOW_MILLIS = 15 * 60_000L;
    private static final int MAX_KEYS = 20_000;

    private record Failures(int count, long windowStart) {}

    private final int maxFailures;
    private final Map<String, Failures> failures = new ConcurrentHashMap<>();

    public LoginThrottle(AppProperties properties) {
        this.maxFailures = Math.max(1, properties.auth().maxFailedLogins());
    }

    public void check(String... keys) {
        long now = System.currentTimeMillis();
        for (String key : keys) {
            Failures f = failures.get(key);
            if (f != null && now - f.windowStart() <= WINDOW_MILLIS && f.count() >= maxFailures) {
                throw new TooManyRequestsException("Too many failed attempts. Try again in a few minutes.");
            }
        }
    }

    public void fail(String... keys) {
        long now = System.currentTimeMillis();
        if (failures.size() > MAX_KEYS) {
            failures.clear();
        }
        for (String key : keys) {
            failures.merge(
                    key,
                    new Failures(1, now),
                    (old, fresh) -> now - old.windowStart() > WINDOW_MILLIS
                            ? fresh
                            : new Failures(old.count() + 1, old.windowStart()));
        }
    }

    public void succeed(String... keys) {
        for (String key : keys) {
            failures.remove(key);
        }
    }
}
