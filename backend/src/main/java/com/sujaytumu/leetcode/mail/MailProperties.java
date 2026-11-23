package com.sujaytumu.leetcode.mail;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

/**
 * Outgoing email through Resend. Leave {@code apiKey} empty to disable sending (messages are only logged).
 * {@code from} must belong to a domain verified in Resend, or be Resend's own test sender, which only
 * delivers to the Resend account owner's address.
 */
@ConfigurationProperties(prefix = "app.mail")
public record MailProperties(
        @DefaultValue("") String apiKey,
        @DefaultValue("LeetCode Practice <onboarding@resend.dev>") String from,
        @DefaultValue("http://localhost:3000") String frontendUrl,
        @DefaultValue("8") int dailyHour,
        @DefaultValue("Asia/Kolkata") String zone) {

    public boolean enabled() {
        return apiKey != null && !apiKey.isBlank();
    }

    /** Frontend origin without a trailing slash, for links inside emails. */
    public String baseUrl() {
        String u = frontendUrl == null || frontendUrl.isBlank() ? "http://localhost:3000" : frontendUrl.trim();
        return u.endsWith("/") ? u.substring(0, u.length() - 1) : u;
    }
}
