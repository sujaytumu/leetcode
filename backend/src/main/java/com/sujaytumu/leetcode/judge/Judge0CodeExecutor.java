package com.sujaytumu.leetcode.judge;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.sujaytumu.leetcode.common.ApiExceptions.ExecutionUnavailableException;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

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
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("source_code", sourceCode);
        body.put("language_id", language.judge0Id());
        body.put("stdin", stdin);
        body.put("cpu_time_limit", cpuTimeLimitSeconds);
        body.put("wall_time_limit", cpuTimeLimitSeconds * 5);

        Judge0Response response;
        try {
            response = client.post()
                    .uri("/submissions?base64_encoded=false&wait=true")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(Judge0Response.class);
        } catch (RestClientException ex) {
            throw new ExecutionUnavailableException("Code execution service is unreachable or returned an error.", ex);
        }
        if (response == null || response.status() == null) {
            throw new ExecutionUnavailableException("Code execution service returned an empty response.");
        }

        int statusId = response.status().id();
        Double time = parseTime(response.time());
        String stdout = nullToEmpty(response.stdout());
        String stderr = nullToEmpty(response.stderr());
        String compile = nullToEmpty(response.compileOutput());

        if (statusId == ACCEPTED) {
            return new ExecutionResult(Status.OK, stdout, stderr, compile, time);
        }
        if (statusId == TIME_LIMIT_EXCEEDED) {
            return new ExecutionResult(Status.TIME_LIMIT_EXCEEDED, stdout, stderr, compile, time);
        }
        if (statusId == COMPILATION_ERROR) {
            return new ExecutionResult(Status.COMPILE_ERROR, stdout, stderr, compile, time);
        }
        if (statusId >= FIRST_RUNTIME_ERROR && statusId <= LAST_RUNTIME_ERROR) {
            String detail = stderr.isBlank() ? nullToEmpty(response.status().description()) : stderr;
            return new ExecutionResult(Status.RUNTIME_ERROR, stdout, detail, compile, time);
        }
        return new ExecutionResult(
                Status.INTERNAL_ERROR, stdout, nullToEmpty(response.message()), compile, time);
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
            String message) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record Judge0Status(int id, String description) {}
}
