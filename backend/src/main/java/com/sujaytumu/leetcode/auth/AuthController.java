package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.auth.AuthService.Session;
import com.sujaytumu.leetcode.common.Headers;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.UUID;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    public record Credentials(String username, String password) {}

    public record PasswordChange(String currentPassword, String newPassword) {}

    public record Me(String username, UUID clientId, Instant createdAt) {}

    private final AuthService service;

    public AuthController(AuthService service) {
        this.service = service;
    }

    /** Claims the caller's anonymous id for a new account, keeping all progress made so far. */
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public Session register(
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @RequestBody Credentials body,
            HttpServletRequest request) {
        return service.register(body.username(), body.password(), clientId, request.getRemoteAddr());
    }

    @PostMapping("/login")
    public Session login(@RequestBody Credentials body, HttpServletRequest request) {
        return service.login(body.username(), body.password(), request.getRemoteAddr());
    }

    @GetMapping("/me")
    public Me me(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization) {
        Account a = service.authenticate(authorization);
        return new Me(a.getUsername(), a.getClientId(), a.getCreatedAt());
    }

    @PostMapping("/password")
    public Session changePassword(
            @RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization,
            @RequestBody PasswordChange body,
            HttpServletRequest request) {
        return service.changePassword(
                authorization, body.currentPassword(), body.newPassword(), request.getRemoteAddr());
    }
}
