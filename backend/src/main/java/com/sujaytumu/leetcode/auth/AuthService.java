package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.common.ApiExceptions.ConflictException;
import com.sujaytumu.leetcode.common.ApiExceptions.UnauthorizedException;
import java.util.Locale;
import java.util.UUID;
import java.util.regex.Pattern;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private static final Pattern USERNAME = Pattern.compile("^[A-Za-z0-9_]{3,20}$");
    private static final String WRONG = "Wrong username or password.";

    public record Session(String token, UUID clientId, String username) {}

    private final AccountRepository accounts;
    private final PasswordHasher hasher;
    private final TokenService tokens;
    private final BoundClients bound;
    private final LoginThrottle throttle;

    public AuthService(
            AccountRepository accounts,
            PasswordHasher hasher,
            TokenService tokens,
            BoundClients bound,
            LoginThrottle throttle) {
        this.accounts = accounts;
        this.hasher = hasher;
        this.tokens = tokens;
        this.bound = bound;
        this.throttle = throttle;
    }

    /** Creates an account that adopts the caller's anonymous id, so existing progress is kept. */
    @Transactional
    public Session register(String rawUsername, String password, UUID clientId, String ip) {
        String username = validUsername(rawUsername);
        validPassword(password, username);
        throttle.check("ip:" + ip);
        if (accounts.existsByClientId(clientId)) {
            throw new ConflictException("This browser already belongs to an account. Log in instead.");
        }
        if (accounts.existsByUsername(username)) {
            throw new ConflictException("That username is taken.");
        }
        Account account;
        try {
            account = accounts.saveAndFlush(new Account(username, hasher.hash(password), clientId));
        } catch (DataIntegrityViolationException e) {
            throw new ConflictException("That username is taken, or this browser already has an account.");
        }
        bound.markBound(clientId);
        return new Session(tokens.issue(account), clientId, username);
    }

    @Transactional(readOnly = true)
    public Session login(String rawUsername, String password, String ip) {
        String username = rawUsername == null ? "" : rawUsername.trim().toLowerCase(Locale.ROOT);
        String userKey = "user:" + username;
        String ipKey = "ip:" + ip;
        throttle.check(userKey, ipKey);
        String supplied = password == null ? "" : password;
        Account account = accounts.findByUsername(username).orElse(null);
        if (account == null) {
            hasher.burn(supplied);
            throttle.fail(userKey, ipKey);
            throw new UnauthorizedException(WRONG);
        }
        if (!hasher.matches(supplied, account.getPasswordHash())) {
            throttle.fail(userKey, ipKey);
            throw new UnauthorizedException(WRONG);
        }
        throttle.succeed(userKey, ipKey);
        return new Session(tokens.issue(account), account.getClientId(), account.getUsername());
    }

    /** Resolves an Authorization header to a live account, or fails with 401. */
    @Transactional(readOnly = true)
    public Account authenticate(String authorization) {
        return accountFor(authorization)
                .orElseThrow(() -> new UnauthorizedException("Please log in again."));
    }

    @Transactional(readOnly = true)
    public java.util.Optional<Account> accountFor(String authorization) {
        if (authorization == null || !authorization.regionMatches(true, 0, "Bearer ", 0, 7)) {
            return java.util.Optional.empty();
        }
        return tokens.verify(authorization.substring(7).trim())
                .flatMap(c -> accounts.findById(c.accountId())
                        .filter(a -> a.getTokenVersion() == c.version() && a.getClientId().equals(c.clientId())));
    }

    @Transactional
    public Session changePassword(String authorization, String current, String next, String ip) {
        Account account = authenticate(authorization);
        throttle.check("user:" + account.getUsername(), "ip:" + ip);
        if (current == null || !hasher.matches(current, account.getPasswordHash())) {
            throttle.fail("user:" + account.getUsername(), "ip:" + ip);
            throw new UnauthorizedException("Current password is wrong.");
        }
        validPassword(next, account.getUsername());
        account.changePassword(hasher.hash(next));
        accounts.save(account);
        return new Session(tokens.issue(account), account.getClientId(), account.getUsername());
    }

    private static String validUsername(String raw) {
        String name = raw == null ? "" : raw.trim();
        if (!USERNAME.matcher(name).matches()) {
            throw new IllegalArgumentException("Username must be 3-20 letters, digits or underscores.");
        }
        return name.toLowerCase(Locale.ROOT);
    }

    private static void validPassword(String password, String username) {
        if (password == null || password.length() < 8 || password.length() > 72) {
            throw new IllegalArgumentException("Password must be 8-72 characters.");
        }
        if (password.equalsIgnoreCase(username)) {
            throw new IllegalArgumentException("Password must not be the same as the username.");
        }
    }
}
