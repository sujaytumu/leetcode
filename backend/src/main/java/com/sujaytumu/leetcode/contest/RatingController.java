package com.sujaytumu.leetcode.contest;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.contest.RatingService.RatingView;
import java.time.Instant;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/profile/rating")
public class RatingController {

    private final RatingService service;

    public RatingController(RatingService service) {
        this.service = service;
    }

    /** Contest rating, global ranking, rating history and the rating distribution for the profile page. */
    @GetMapping
    public RatingView rating(@RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.view(clientId, Instant.now());
    }
}
