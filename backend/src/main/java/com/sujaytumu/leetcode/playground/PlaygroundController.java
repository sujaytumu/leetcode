package com.sujaytumu.leetcode.playground;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.common.RunRateLimiter;
import com.sujaytumu.leetcode.judge.CodeExecutor;
import com.sujaytumu.leetcode.judge.CodeExecutor.ExecutionResult;
import com.sujaytumu.leetcode.judge.Language;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.UUID;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Free-form code runner: executes a program once with the given stdin. Nothing is stored or judged. */
@RestController
@RequestMapping("/api/playground")
public class PlaygroundController {

    private static final int MAX_OUTPUT = 10_000;

    public record RunRequest(
            @NotNull Language language,
            @NotBlank @Size(max = 65536) String code,
            @Size(max = 20000) String stdin) {}

    /** {@code status} is one of OK, COMPILE_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, INTERNAL_ERROR. */
    public record RunResult(
            String status, String stdout, String stderr, String compileOutput, Integer timeMs, Integer memoryKb) {}

    private final CodeExecutor executor;
    private final RunRateLimiter rateLimiter;

    public PlaygroundController(CodeExecutor executor, RunRateLimiter rateLimiter) {
        this.executor = executor;
        this.rateLimiter = rateLimiter;
    }

    @PostMapping("/run")
    public RunResult run(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @Valid @RequestBody RunRequest request) {
        rateLimiter.check(clientId);
        String stdin = request.stdin() == null ? "" : request.stdin();
        ExecutionResult r = executor.execute(request.language(), request.code(), stdin);
        Integer ms = r.timeSeconds() == null ? null : (int) Math.round(r.timeSeconds() * 1000);
        return new RunResult(r.status().name(), clip(r.stdout()), clip(r.stderr()), clip(r.compileOutput()), ms, r.memoryKb());
    }

    private static String clip(String s) {
        if (s == null) {
            return "";
        }
        return s.length() <= MAX_OUTPUT ? s : s.substring(0, MAX_OUTPUT) + "\n… output truncated";
    }
}
