package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.study.RecommendationService.Recommendations;
import java.time.Instant;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

    private final RecommendationService service;

    public RecommendationController(RecommendationService service) {
        this.service = service;
    }

    @GetMapping
    public Recommendations recommendations(@RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.recommend(clientId, Instant.now());
    }
}
