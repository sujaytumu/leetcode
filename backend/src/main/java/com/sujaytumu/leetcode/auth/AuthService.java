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
    private static final Pattern EMAIL = Pattern.compile("^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*\\.[A-Za-z]{2,}$");
    private static final String WRONG = "Wrong email or password.";

    public record Session(String token, UUID clientId, String username, String email) {}

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
    public Session register(String rawEmail, String rawUsername, String password, boolean dailyEmail, UUID clientId, String ip) {
        String email = validEmail(rawEmail);
        String username = rawUsername == null || rawUsername.isBlank() ? freeUsername(email) : validUsername(rawUsername);
        validPassword(password, username, email);
        throttle.check("ip:" + ip);
        if (accounts.existsByClientId(clientId)) {
            throw new ConflictException("This browser already belongs to an account. Log in instead.");
        }
        if (accounts.existsByEmail(email)) {
            throw new ConflictException("An account with that email already exists. Log in instead.");
        }
        if (accounts.existsByUsername(username)) {
            throw new ConflictException("That username is taken.");
        }
        Account account;
        try {
            Account fresh = new Account(email, username, hasher.hash(password), clientId);
            fresh.setDailyEmail(dailyEmail);
            account = accounts.saveAndFlush(fresh);
        } catch (DataIntegrityViolationException e) {
            throw new ConflictException("That email or username is taken, or this browser already has an account.");
        }
        bound.markBound(clientId);
        return new Session(tokens.issue(account), clientId, username, email);
    }

    @Transactional(readOnly = true)
    public Session login(String rawIdentifier, String password, String ip) {
        String identifier = rawIdentifier == null ? "" : rawIdentifier.trim().toLowerCase(Locale.ROOT);
        String userKey = "user:" + identifier;
        String ipKey = "ip:" + ip;
        throttle.check(userKey, ipKey);
        String supplied = password == null ? "" : password;
        Account account = (identifier.contains("@") ? accounts.findByEmail(identifier) : accounts.findByUsername(identifier)).orElse(null);
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
        return new Session(tokens.issue(account), account.getClientId(), account.getUsername(), account.getEmail());
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
        validPassword(next, account.getUsername(), account.getEmail());
        account.changePassword(hasher.hash(next));
        accounts.save(account);
        return new Session(tokens.issue(account), account.getClientId(), account.getUsername(), account.getEmail());
    }

    public record EmailPrefs(String email, boolean dailyEmail) {}

    @Transactional(readOnly = true)
    public EmailPrefs emailPrefs(String authorization) {
        Account a = authenticate(authorization);
        return new EmailPrefs(a.getEmail(), a.isDailyEmail());
    }

    @Transactional
    public EmailPrefs setDailyEmail(String authorization, boolean on) {
        Account a = authenticate(authorization);
        if (on && a.getEmail() == null) {
            throw new IllegalArgumentException("Add an email address to your account first.");
        }
        a.setDailyEmail(on);
        accounts.save(a);
        return new EmailPrefs(a.getEmail(), a.isDailyEmail());
    }

    /** One-click unsubscribe from the link in a daily email; works without logging in. */
    @Transactional
    public void unsubscribe(String token) {
        long id = tokens.verifyUnsubscribe(token)
                .orElseThrow(() -> new IllegalArgumentException("This unsubscribe link is not valid."));
        accounts.findById(id).ifPresent(a -> {
            a.setDailyEmail(false);
            accounts.save(a);
        });
    }

    private static String validUsername(String raw) {
        String name = raw == null ? "" : raw.trim();
        if (!USERNAME.matcher(name).matches()) {
            throw new IllegalArgumentException("Username must be 3-20 letters, digits or underscores.");
        }
        return name.toLowerCase(Locale.ROOT);
    }

    private static String validEmail(String raw) {
        String email = raw == null ? "" : raw.trim().toLowerCase(Locale.ROOT);
        if (email.length() > 254 || !EMAIL.matcher(email).matches()) {
            throw new IllegalArgumentException("Enter a valid email address.");
        }
        return email;
    }

    /** A free 3-20 character username derived from the email's local part, for sign-ups that do not pick one. */
    private String freeUsername(String email) {
        String base = email.substring(0, email.indexOf('@')).replaceAll("[^a-z0-9_]", "_");
        if (base.length() > 14) {
            base = base.substring(0, 14);
        }
        while (base.length() < 3) {
            base += "_";
        }
        String candidate = base;
        while (accounts.existsByUsername(candidate)) {
            candidate = base + java.util.concurrent.ThreadLocalRandom.current().nextInt(100000, 999999);
        }
        return candidate;
    }

    static void validPassword(String password, String username, String email) {
        if (password == null || password.length() < 8 || password.length() > 72) {
            throw new IllegalArgumentException("Password must be 8-72 characters.");
        }
        if (password.equalsIgnoreCase(username) || (email != null && password.equalsIgnoreCase(email))) {
            throw new IllegalArgumentException("Password must not be the same as the username or email.");
        }
    }
}
