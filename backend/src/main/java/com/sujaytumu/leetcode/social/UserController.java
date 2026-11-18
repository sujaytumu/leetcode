package com.sujaytumu.leetcode.social;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.contest.RatingService;
import com.sujaytumu.leetcode.contest.RatingService.RatingView;
import com.sujaytumu.leetcode.social.PublicProfileService.PublicProfile;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.ZoneId;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class UserController {

    private final PublicProfileService service;
    private final RatingService ratings;

    public UserController(PublicProfileService service, RatingService ratings) {
        this.service = service;
        this.ratings = ratings;
    }

    @GetMapping("/api/users/{username}")
    public PublicProfile profile(
            @PathVariable String username,
            @RequestParam(defaultValue = "UTC") String zone,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID viewer) {
        ZoneId zoneId;
        try {
            zoneId = ZoneId.of(zone);
        } catch (DateTimeException ex) {
            throw new IllegalArgumentException("Unknown time zone: " + zone);
        }
        return service.get(username, viewer, zoneId);
    }

    @GetMapping("/api/users/{username}/rating")
    public RatingView rating(@PathVariable String username) {
        return ratings.view(service.idOf(username), Instant.now());
    }

    @PutMapping("/api/users/{username}/follow")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void follow(@PathVariable String username, @RequestHeader(Headers.CLIENT_ID) UUID viewer) {
        service.follow(viewer, username);
    }

    @DeleteMapping("/api/users/{username}/follow")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void unfollow(@PathVariable String username, @RequestHeader(Headers.CLIENT_ID) UUID viewer) {
        service.unfollow(viewer, username);
    }
}
