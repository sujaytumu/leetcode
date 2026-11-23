package com.sujaytumu.leetcode.profileinfo;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoService.ProfileInfoView;
import java.util.UUID;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
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

    /** Body: {"photo": "data:image/jpeg;base64,..."}. */
    @PutMapping("/photo")
    public ProfileInfoView setPhoto(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody Map<String, String> body) {
        return service.setPhoto(clientId, body.get("photo"));
    }

    @DeleteMapping("/photo")
    public ProfileInfoView removePhoto(@RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.setPhoto(clientId, null);
    }

    /** Public image for <img> tags: /api/profile/info/avatar/{client id or username}?v=version. */
    @GetMapping("/avatar/{key}")
    public ResponseEntity<byte[]> avatar(@PathVariable String key) {
        return service.photoOf(key)
                .map(p -> ResponseEntity.ok().contentType(MediaType.parseMediaType(p.getKey()))
                        .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS).cachePublic()).body(p.getValue()))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
