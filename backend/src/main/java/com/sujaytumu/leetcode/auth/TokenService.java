package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.config.AppProperties;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;
import java.util.Optional;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Stateless login tokens: {@code base64url(accountId.clientId.tokenVersion.expiryEpoch).base64url(hmacSha256)}.
 * No dependency needed; the signature covers the whole payload.
 */
@Component
public class TokenService {

    private static final Logger log = LoggerFactory.getLogger(TokenService.class);
    private static final String HMAC = "HmacSHA256";

    public record Claims(long accountId, UUID clientId, int version) {}

    private final byte[] key;
    private final long ttlSeconds;

    public TokenService(AppProperties properties) {
        String secret = properties.auth().secret();
        if (secret == null || secret.length() < 32) {
            byte[] random = new byte[32];
            new SecureRandom().nextBytes(random);
            this.key = random;
            log.warn("AUTH_SECRET is not set (or shorter than 32 chars): login tokens will be invalid after a restart.");
        } else {
            this.key = secret.getBytes(StandardCharsets.UTF_8);
        }
        this.ttlSeconds = Math.max(1, properties.auth().tokenDays()) * 86_400L;
    }

    public String issue(Account account) {
        long expiry = Instant.now().getEpochSecond() + ttlSeconds;
        String payload = account.getId() + "." + account.getClientId() + "." + account.getTokenVersion() + "." + expiry;
        Base64.Encoder b64 = Base64.getUrlEncoder().withoutPadding();
        String body = b64.encodeToString(payload.getBytes(StandardCharsets.UTF_8));
        return body + "." + b64.encodeToString(sign(body));
    }

    public Optional<Claims> verify(String token) {
        try {
            int dot = token.indexOf('.');
            if (dot <= 0 || dot == token.length() - 1) {
                return Optional.empty();
            }
            String body = token.substring(0, dot);
            byte[] given = Base64.getUrlDecoder().decode(token.substring(dot + 1));
            if (!MessageDigest.isEqual(given, sign(body))) {
                return Optional.empty();
            }
            String[] f = new String(Base64.getUrlDecoder().decode(body), StandardCharsets.UTF_8).split("\\.");
            if (f.length != 4 || Long.parseLong(f[3]) < Instant.now().getEpochSecond()) {
                return Optional.empty();
            }
            return Optional.of(new Claims(Long.parseLong(f[0]), UUID.fromString(f[1]), Integer.parseInt(f[2])));
        } catch (IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    /** Signed, non-expiring token for the one-click unsubscribe link in daily emails. */
    public String unsubscribeToken(long accountId) {
        Base64.Encoder b64 = Base64.getUrlEncoder().withoutPadding();
        String body = b64.encodeToString(("unsub:" + accountId).getBytes(StandardCharsets.UTF_8));
        return body + "." + b64.encodeToString(sign(body));
    }

    /** The account id inside a valid unsubscribe token, if the signature checks out. */
    public java.util.OptionalLong verifyUnsubscribe(String token) {
        try {
            int dot = token == null ? -1 : token.indexOf('.');
            if (dot <= 0 || dot == token.length() - 1) {
                return java.util.OptionalLong.empty();
            }
            String body = token.substring(0, dot);
            byte[] given = Base64.getUrlDecoder().decode(token.substring(dot + 1));
            if (!MessageDigest.isEqual(given, sign(body))) {
                return java.util.OptionalLong.empty();
            }
            String plain = new String(Base64.getUrlDecoder().decode(body), StandardCharsets.UTF_8);
            return plain.startsWith("unsub:") ? java.util.OptionalLong.of(Long.parseLong(plain.substring(6))) : java.util.OptionalLong.empty();
        } catch (IllegalArgumentException e) {
            return java.util.OptionalLong.empty();
        }
    }

    private byte[] sign(String body) {
        try {
            Mac mac = Mac.getInstance(HMAC);
            mac.init(new SecretKeySpec(key, HMAC));
            return mac.doFinal(body.getBytes(StandardCharsets.UTF_8));
        } catch (java.security.GeneralSecurityException e) {
            throw new IllegalStateException("HMAC unavailable", e);
        }
    }
}
