package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.auth.AuthService.Session;
import com.sujaytumu.leetcode.mail.EmailService;
import com.sujaytumu.leetcode.mail.EmailTemplates;
import com.sujaytumu.leetcode.mail.MailProperties;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Locale;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** "Forgot password": emails a single-use link valid for 30 minutes, then sets the new password and signs in. */
@Service
public class PasswordResetService {

    private static final Duration TTL = Duration.ofMinutes(30);
    private static final String INVALID = "This reset link is invalid or has expired. Request a new one.";

    private final AccountRepository accounts;
    private final PasswordResetTokenRepository resetTokens;
    private final PasswordHasher hasher;
    private final TokenService tokens;
    private final LoginThrottle throttle;
    private final EmailService mail;
    private final MailProperties props;
    private final SecureRandom random = new SecureRandom();

    public PasswordResetService(
            AccountRepository accounts,
            PasswordResetTokenRepository resetTokens,
            PasswordHasher hasher,
            TokenService tokens,
            LoginThrottle throttle,
            EmailService mail,
            MailProperties props) {
        this.accounts = accounts;
        this.resetTokens = resetTokens;
        this.hasher = hasher;
        this.tokens = tokens;
        this.throttle = throttle;
        this.mail = mail;
        this.props = props;
    }

    /** Never reveals whether the email has an account: every request counts against the same limits and answers alike. */
    @Transactional
    public void request(String rawEmail, String ip) {
        String ipKey = "reset-ip:" + ip;
        throttle.check(ipKey);
        throttle.fail(ipKey);
        String email = rawEmail == null ? "" : rawEmail.trim().toLowerCase(Locale.ROOT);
        if (email.isEmpty() || email.length() > 254) {
            return;
        }
        String mailKey = "reset-mail:" + email;
        throttle.check(mailKey);
        throttle.fail(mailKey);
        resetTokens.deleteByExpiresAtBefore(Instant.now());
        accounts.findByEmail(email).ifPresent(account -> {
            resetTokens.deleteByAccountId(account.getId());
            byte[] bytes = new byte[32];
            random.nextBytes(bytes);
            String raw = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
            resetTokens.save(new PasswordResetToken(account.getId(), sha256(raw), Instant.now().plus(TTL)));
            String link = props.baseUrl() + "/reset-password?token=" + raw;
            mail.sendAsync(EmailTemplates.passwordReset(email, link, (int) TTL.toMinutes()));
        });
    }

    @Transactional
    public Session reset(String rawToken, String newPassword, String ip) {
        String ipKey = "reset-try:" + ip;
        throttle.check(ipKey);
        PasswordResetToken found = rawToken == null || rawToken.isBlank()
                ? null
                : resetTokens.findByTokenHash(sha256(rawToken.trim())).orElse(null);
        if (found == null || found.getExpiresAt().isBefore(Instant.now())) {
            throttle.fail(ipKey);
            if (found != null) {
                resetTokens.delete(found);
            }
            throw new IllegalArgumentException(INVALID);
        }
        Account account = accounts.findById(found.getAccountId()).orElse(null);
        if (account == null) {
            resetTokens.delete(found);
            throw new IllegalArgumentException(INVALID);
        }
        AuthService.validPassword(newPassword, account.getUsername(), account.getEmail());
        account.changePassword(hasher.hash(newPassword)); // also bumps the token version: every old session ends
        accounts.save(account);
        resetTokens.deleteByAccountId(account.getId());
        throttle.succeed(ipKey);
        return new Session(tokens.issue(account), account.getClientId(), account.getUsername(), account.getEmail());
    }

    private static String sha256(String value) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        }
    }
}
