package com.sujaytumu.leetcode.progress;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.progress.ProfileService.ProfileView;
import java.time.DateTimeException;
import java.time.ZoneId;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/profile")
public class ProfileController {

    private final ProfileService service;

    public ProfileController(ProfileService service) {
        this.service = service;
    }

    /** {@code zone} is an IANA id such as Asia/Kolkata so days roll over at the user's midnight; default UTC. */
    @GetMapping
    public ProfileView profile(
            @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestParam(defaultValue = "UTC") String zone) {
        ZoneId zoneId;
        try {
            zoneId = ZoneId.of(zone);
        } catch (DateTimeException ex) {
            throw new IllegalArgumentException("Unknown time zone: " + zone);
        }
        return service.profile(clientId, zoneId);
    }
}
