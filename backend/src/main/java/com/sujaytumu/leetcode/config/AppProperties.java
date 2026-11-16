package com.sujaytumu.leetcode.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "app")
public record AppProperties(
        @DefaultValue Cors cors,
        @DefaultValue Seed seed,
        @DefaultValue RateLimit rateLimit,
        @DefaultValue Judge0 judge0) {

    public record Cors(@DefaultValue("http://localhost:3000") List<String> allowedOrigins) {}

    public record Seed(@DefaultValue("true") boolean enabled) {}

    public record RateLimit(@DefaultValue("20") int runsPerMinute) {}

    public record Judge0(
            @DefaultValue("") String baseUrl,
            @DefaultValue("") String authToken,
            @DefaultValue("2.0") double cpuTimeLimitSeconds,
            @DefaultValue("20") int readTimeoutSeconds) {

        public boolean enabled() {
            return baseUrl != null && !baseUrl.isBlank();
        }
    }
}
