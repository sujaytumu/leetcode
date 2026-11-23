package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.auth.AuthService.EmailPrefs;
import com.sujaytumu.leetcode.auth.AuthService.Session;
import com.sujaytumu.leetcode.common.Headers;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.UUID;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    /** Sign up with {@code email} (+ optional {@code username}); log in with {@code email} or, for older accounts, {@code username}. */
    public record Credentials(String email, String username, String password, Boolean dailyEmail) {}

    public record Forgot(String email) {}

    public record Reset(String token, String password) {}

    public record Unsubscribe(String token) {}

    public record Prefs(Boolean dailyEmail) {}

    public record Ack(boolean ok) {}

    public record PasswordChange(String currentPassword, String newPassword) {}

    public record Me(String username, String email, UUID clientId, Instant createdAt, boolean dailyEmail) {}

    private final AuthService service;
    private final PasswordResetService resets;

    public AuthController(AuthService service, PasswordResetService resets) {
        this.service = service;
        this.resets = resets;
    }

    /** Claims the caller's anonymous id for a new account, keeping all progress made so far. */
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public Session register(
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @RequestBody Credentials body,
            HttpServletRequest request) {
        return service.register(
                body.email(), body.username(), body.password(), Boolean.TRUE.equals(body.dailyEmail()), clientId, request.getRemoteAddr());
    }

    @PostMapping("/login")
    public Session login(@RequestBody Credentials body, HttpServletRequest request) {
        String identifier = body.email() != null && !body.email().isBlank() ? body.email() : body.username();
        return service.login(identifier, body.password(), request.getRemoteAddr());
    }

    @GetMapping("/me")
    public Me me(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization) {
        Account a = service.authenticate(authorization);
        return new Me(a.getUsername(), a.getEmail(), a.getClientId(), a.getCreatedAt(), a.isDailyEmail());
    }

    @PostMapping("/password")
    public Session changePassword(
            @RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization,
            @RequestBody PasswordChange body,
            HttpServletRequest request) {
        return service.changePassword(
                authorization, body.currentPassword(), body.newPassword(), request.getRemoteAddr());
    }

    /** "Sign out everywhere": every other device must log in again; the response keeps this one signed in. */
    @PostMapping("/logout-all")
    public Session logoutAll(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization) {
        return service.logoutEverywhere(authorization);
    }

    /** Always answers ok, whether or not the email has an account, so it cannot be used to look accounts up. */
    @PostMapping("/forgot")
    public Ack forgot(@RequestBody Forgot body, HttpServletRequest request) {
        resets.request(body.email(), request.getRemoteAddr());
        return new Ack(true);
    }

    /** Sets a new password from an emailed link and signs the caller in. */
    @PostMapping("/reset")
    public Session reset(@RequestBody Reset body, HttpServletRequest request) {
        return resets.reset(body.token(), body.password(), request.getRemoteAddr());
    }

    @GetMapping("/email-prefs")
    public EmailPrefs emailPrefs(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization) {
        return service.emailPrefs(authorization);
    }

    @PutMapping("/email-prefs")
    public EmailPrefs setEmailPrefs(
            @RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorization,
            @RequestBody Prefs body) {
        return service.setDailyEmail(authorization, Boolean.TRUE.equals(body.dailyEmail()));
    }

    /** One-click unsubscribe from a daily email; the signed token in the link is the proof, so no login is needed. */
    @PostMapping("/unsubscribe")
    public Ack unsubscribe(@RequestBody Unsubscribe body) {
        service.unsubscribe(body.token());
        return new Ack(true);
    }
}
