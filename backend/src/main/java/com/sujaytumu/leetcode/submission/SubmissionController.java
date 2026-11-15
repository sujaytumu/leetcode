package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.submission.SubmissionDtos.RunRequest;
import com.sujaytumu.leetcode.submission.SubmissionDtos.RunResponse;
import com.sujaytumu.leetcode.submission.SubmissionDtos.SubmissionView;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/problems/{slug}")
public class SubmissionController {

    private final SubmissionService service;

    public SubmissionController(SubmissionService service) {
        this.service = service;
    }

    @PostMapping("/run")
    public RunResponse run(
            @PathVariable String slug,
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @Valid @RequestBody RunRequest request) {
        return service.run(slug, clientId, request.language(), request.code());
    }

    @PostMapping("/submit")
    public RunResponse submit(
            @PathVariable String slug,
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @Valid @RequestBody RunRequest request) {
        return service.submit(slug, clientId, request.language(), request.code());
    }

    @GetMapping("/submissions")
    public List<SubmissionView> history(
            @PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.history(slug, clientId);
    }
}
