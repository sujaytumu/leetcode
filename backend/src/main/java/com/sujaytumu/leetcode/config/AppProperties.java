package com.sujaytumu.leetcode.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConfigurationProperties(prefix = "app")
public record AppProperties(
        @DefaultValue Cors cors,
        @DefaultValue Seed seed,
        @DefaultValue RateLimit rateLimit,
        @DefaultValue Judge0 judge0,
        @DefaultValue Auth auth) {

    public record Cors(@DefaultValue("http://localhost:3000") List<String> allowedOrigins) {}

    /** secret signs login tokens; set AUTH_SECRET in production or tokens reset on every restart. */
    public record Auth(
            @DefaultValue("") String secret,
            @DefaultValue("30") int tokenDays,
            @DefaultValue("8") int maxFailedLogins) {}

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
