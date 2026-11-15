package com.sujaytumu.leetcode.common;

import com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException;
import com.sujaytumu.leetcode.config.AppProperties;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/** Sliding-window limiter protecting the code execution backend from abuse. */
@Component
public class RunRateLimiter {

    private static final long WINDOW_MILLIS = 60_000;
    private static final int CLEANUP_THRESHOLD = 10_000;

    private final int limit;
    private final Map<UUID, Deque<Long>> hits = new ConcurrentHashMap<>();

    public RunRateLimiter(AppProperties properties) {
        this.limit = Math.max(1, properties.rateLimit().runsPerMinute());
    }

    public void check(UUID clientId) {
        long now = System.currentTimeMillis();
        Deque<Long> window = hits.computeIfAbsent(clientId, id -> new ArrayDeque<>());
        synchronized (window) {
            while (!window.isEmpty() && now - window.peekFirst() > WINDOW_MILLIS) {
                window.pollFirst();
            }
            if (window.size() >= limit) {
                throw new TooManyRequestsException(
                        "Too many runs. Limit is " + limit + " per minute; try again shortly.");
            }
            window.addLast(now);
        }
        if (hits.size() > CLEANUP_THRESHOLD) {
            hits.entrySet().removeIf(entry -> {
                synchronized (entry.getValue()) {
                    Long last = entry.getValue().peekLast();
                    return last == null || now - last > WINDOW_MILLIS;
                }
            });
        }
    }
}
