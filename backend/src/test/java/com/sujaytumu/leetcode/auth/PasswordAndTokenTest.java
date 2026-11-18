package com.sujaytumu.leetcode.auth;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sujaytumu.leetcode.config.AppProperties;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class PasswordAndTokenTest {

    private static AppProperties props(String secret, int days) {
        return new AppProperties(
                new AppProperties.Cors(List.of()),
                new AppProperties.Seed(false),
                new AppProperties.RateLimit(20),
                new AppProperties.Judge0("", "", 2.0, 20),
                new AppProperties.Auth(secret, days, 3));
    }

    @Test
    void hashesAreSaltedAndVerify() {
        PasswordHasher hasher = new PasswordHasher();
        String a = hasher.hash("correct horse");
        String b = hasher.hash("correct horse");
        assertNotEquals(a, b);
        assertTrue(hasher.matches("correct horse", a));
        assertFalse(hasher.matches("Correct horse", a));
        assertFalse(hasher.matches("correct horse", "garbage"));
    }

    @Test
    void tokensRoundTripAndRejectTampering() {
        TokenService tokens = new TokenService(props("x".repeat(40), 30));
        Account account = new Account("sujay", "hash", UUID.randomUUID());
        String token = tokens.issue(account);
        var claims = tokens.verify(token).orElseThrow();
        assertEquals(account.getClientId(), claims.clientId());

        assertTrue(tokens.verify(token + "a").isEmpty());
        assertTrue(tokens.verify("a" + token).isEmpty());
        assertTrue(tokens.verify("not-a-token").isEmpty());
        TokenService other = new TokenService(props("y".repeat(40), 30));
        assertTrue(other.verify(token).isEmpty());
    }

    @Test
    void loginThrottleLocksAfterTooManyFailures() {
        LoginThrottle throttle = new LoginThrottle(props("", 30));
        throttle.fail("user:bob");
        throttle.fail("user:bob");
        throttle.check("user:bob");
        throttle.fail("user:bob");
        org.junit.jupiter.api.Assertions.assertThrows(
                com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException.class,
                () -> throttle.check("user:bob"));
        throttle.succeed("user:bob");
        throttle.check("user:bob");
    }
}
