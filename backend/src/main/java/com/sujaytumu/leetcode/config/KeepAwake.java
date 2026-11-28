package com.sujaytumu.leetcode.config;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * Render's free web service sleeps after 15 minutes without inbound traffic, and waking this app takes minutes.
 * While running, it therefore requests its own public URL every 10 minutes. The scheduled GitHub workflow cannot do
 * this alone: GitHub delays frequent schedules by hours. The path is one that never touches the database, so the
 * database can still suspend. Off when no URL is known (local runs and tests); set KEEP_AWAKE=false to turn it off.
 */
@Component
public class KeepAwake {

    private static final Logger log = LoggerFactory.getLogger(KeepAwake.class);

    private final URI target;
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    public KeepAwake(
            @Value("${app.keep-awake.enabled:true}") boolean enabled,
            @Value("${app.keep-awake.url:}") String url) {
        this.target = enabled && !url.isBlank() ? URI.create(url.replaceAll("/+$", "") + "/api/meta") : null;
    }

    @Scheduled(fixedDelay = 10 * 60_000L, initialDelay = 60_000L)
    public void ping() {
        if (target == null) {
            return;
        }
        HttpRequest request = HttpRequest.newBuilder(target).timeout(Duration.ofSeconds(20)).build();
        try {
            int status = http.send(request, HttpResponse.BodyHandlers.discarding()).statusCode();
            if (status >= 400) {
                log.warn("Keep-awake ping to {} answered HTTP {}", target, status);
            }
        } catch (java.io.IOException e) {
            log.warn("Keep-awake ping to {} failed: {}", target, e.toString());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
