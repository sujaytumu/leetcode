package com.sujaytumu.leetcode.progress;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.progress.ProgressService.ProgressSummary;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/progress")
public class ProgressController {

    private final ProgressService service;

    public ProgressController(ProgressService service) {
        this.service = service;
    }

    @GetMapping
    public ProgressSummary summary(@RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.summary(clientId);
    }
}
