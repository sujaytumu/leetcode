package com.sujaytumu.leetcode.contest;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.contest.ContestService.Overview;
import com.sujaytumu.leetcode.contest.ContestService.Standings;
import java.time.Instant;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/contests")
public class ContestController {

    private final ContestService service;

    public ContestController(ContestService service) {
        this.service = service;
    }

    @GetMapping
    public Overview overview() {
        return service.overview(Instant.now());
    }

    @GetMapping("/{id}")
    public Standings standings(
            @PathVariable long id, @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.standings(id, clientId, Instant.now());
    }
}
