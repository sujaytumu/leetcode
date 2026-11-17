package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.submission.SubmissionDtos.SubmissionStats;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/submissions")
public class SubmissionStatsController {

    private final SubmissionService service;

    public SubmissionStatsController(SubmissionService service) {
        this.service = service;
    }

    /** Runtime and memory distribution of an accepted submission against others in the same language. */
    @GetMapping("/{id}/stats")
    public SubmissionStats stats(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.stats(id, clientId);
    }
}
