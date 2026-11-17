package com.sujaytumu.leetcode.profileinfo;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoService.ProfileInfoView;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/profile/info")
public class ProfileInfoController {

    private final ProfileInfoService service;

    public ProfileInfoController(ProfileInfoService service) {
        this.service = service;
    }

    @GetMapping
    public ProfileInfoView get(@RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.get(clientId);
    }

    @PutMapping
    public ProfileInfoView update(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody ProfileInfoView body) {
        return service.update(clientId, body);
    }
}
