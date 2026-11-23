package com.sujaytumu.leetcode.judge;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.sujaytumu.leetcode.common.ApiExceptions.ExecutionUnavailableException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

/** Executes code on a Judge0 CE instance (https://github.com/judge0/judge0) using synchronous submissions. */
public class Judge0CodeExecutor implements CodeExecutor {

    private static final int ACCEPTED = 3;
    private static final int TIME_LIMIT_EXCEEDED = 5;
    private static final int COMPILATION_ERROR = 6;
    private static final int FIRST_RUNTIME_ERROR = 7;
    private static final int LAST_RUNTIME_ERROR = 12;

    private final RestClient client;
    private final double cpuTimeLimitSeconds;

    public Judge0CodeExecutor(RestClient client, double cpuTimeLimitSeconds) {
        this.client = client;
        this.cpuTimeLimitSeconds = cpuTimeLimitSeconds;
    }

    @Override
    public ExecutionResult execute(Language language, String sourceCode, String stdin) {
        // Base64 both ways: Judge0 answers 400 for stdin/source holding characters it cannot round-trip as plain JSON text.
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("source_code", encode(sourceCode));
        body.put("language_id", language.judge0Id());
        body.put("stdin", encode(stdin));
        body.put("cpu_time_limit", cpuTimeLimitSeconds);
        body.put("wall_time_limit", cpuTimeLimitSeconds * 5);

        Judge0Response response = submit(body);
        if (response == null || response.status() == null) {
            throw new ExecutionUnavailableException("Code execution service returned an empty response.");
        }

        int statusId = response.status().id();
        Double time = parseTime(response.time());
        Integer memory = response.memory();
        String stdout = decode(response.stdout());
        String stderr = decode(response.stderr());
        String compile = decode(response.compileOutput());

        if (statusId == ACCEPTED) {
            return new ExecutionResult(Status.OK, stdout, stderr, compile, time, memory);
        }
        if (statusId == TIME_LIMIT_EXCEEDED) {
            return new ExecutionResult(Status.TIME_LIMIT_EXCEEDED, stdout, stderr, compile, time, memory);
        }
        if (statusId == COMPILATION_ERROR) {
            return new ExecutionResult(Status.COMPILE_ERROR, stdout, stderr, compile, time, memory);
        }
        if (statusId >= FIRST_RUNTIME_ERROR && statusId <= LAST_RUNTIME_ERROR) {
            String detail = stderr.isBlank() ? nullToEmpty(response.status().description()) : stderr;
            return new ExecutionResult(Status.RUNTIME_ERROR, stdout, detail, compile, time, memory);
        }
        return new ExecutionResult(
                Status.INTERNAL_ERROR, stdout, decode(response.message()), compile, time, memory);
    }

    private static final int MAX_ATTEMPTS = 3;

    /** Posts a synchronous submission, retrying briefly when the free public instance is rate limited or busy. */
    private Judge0Response submit(Map<String, Object> body) {
        ExecutionUnavailableException last = null;
        boolean limitsDropped = false;
        for (int attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
            try {
                return client.post()
                        .uri("/submissions?base64_encoded=true&wait=true")
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(body)
                        .retrieve()
                        .body(Judge0Response.class);
            } catch (RestClientResponseException ex) {
                int status = ex.getStatusCode().value();
                if (status == 429) {
                    last = new ExecutionUnavailableException(
                            "The free code-execution service is rate limited right now. Wait a few seconds and try again.", ex);
                } else if (status == 502 || status == 503 || status == 504) {
                    last = new ExecutionUnavailableException(
                            "The code-execution service is busy or restarting (HTTP " + status + "). Try again shortly.", ex);
                } else if (status == 400 && !limitsDropped) {
                    // Some Judge0 instances refuse custom time limits; the instance's own defaults still apply.
                    limitsDropped = true;
                    body.remove("cpu_time_limit");
                    body.remove("wall_time_limit");
                    last = new ExecutionUnavailableException("The code-execution service rejected the request (HTTP 400).", ex);
                    continue;
                } else {
                    String detail = ex.getResponseBodyAsString();
                    if (detail != null && detail.length() > 300) {
                        detail = detail.substring(0, 300);
                    }
                    throw new ExecutionUnavailableException(
                            "The code-execution service rejected the request (HTTP " + status + ")"
                                    + (detail == null || detail.isBlank() ? "." : ": " + detail), ex);
                }
                if (attempt < MAX_ATTEMPTS) {
                    pause(1500L * attempt);
                }
            } catch (RestClientException ex) {
                throw new ExecutionUnavailableException(
                        "The code-execution service is unreachable or timed out. Try again shortly.", ex);
            }
        }
        throw last;
    }

    private static void pause(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        }
    }

    @Override
    public Health health() {
        try {
            client.get().uri("/about").retrieve().toBodilessEntity();
            return new Health(true, true, "judge0", "Code execution is available.");
        } catch (RestClientException ex) {
            return new Health(true, false, "judge0", "The code-execution service is not responding right now.");
        }
    }

    private static Double parseTime(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    private static String encode(String value) {
        return Base64.getEncoder().encodeToString(nullToEmpty(value).getBytes(StandardCharsets.UTF_8));
    }

    /** Judge0 returns output fields base64-encoded (with line breaks) when base64_encoded=true. */
    private static String decode(String value) {
        if (value == null || value.isBlank()) {
            return "";
        }
        try {
            return new String(Base64.getMimeDecoder().decode(value), StandardCharsets.UTF_8);
        } catch (IllegalArgumentException ex) {
            return value;
        }
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    record Judge0Response(
            Judge0Status status,
            String stdout,
            String stderr,
            @JsonProperty("compile_output") String compileOutput,
            String time,
            Integer memory,
            String message) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record Judge0Status(int id, String description) {}
}
