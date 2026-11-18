package com.sujaytumu.leetcode.auth;

import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/**
 * Fast answer to "does this client id belong to an account?" so anonymous traffic does not hit the database
 * on every request. Bound ids never become unbound; "not bound" answers expire so a stale answer is short-lived.
 */
@Component
public class BoundClients {

    private static final long NEGATIVE_TTL_MILLIS = 60_000;
    private static final int MAX_ENTRIES = 50_000;

    private final AccountRepository accounts;
    private final Set<UUID> bound = ConcurrentHashMap.newKeySet();
    private final Map<UUID, Long> notBoundUntil = new ConcurrentHashMap<>();

    public BoundClients(AccountRepository accounts) {
        this.accounts = accounts;
    }

    public boolean isBound(UUID clientId) {
        if (bound.contains(clientId)) {
            return true;
        }
        long now = System.currentTimeMillis();
        Long until = notBoundUntil.get(clientId);
        if (until != null && until > now) {
            return false;
        }
        boolean exists = accounts.existsByClientId(clientId);
        if (exists) {
            markBound(clientId);
        } else {
            if (notBoundUntil.size() > MAX_ENTRIES) {
                notBoundUntil.clear();
            }
            notBoundUntil.put(clientId, now + NEGATIVE_TTL_MILLIS);
        }
        return exists;
    }

    public void markBound(UUID clientId) {
        bound.add(clientId);
        notBoundUntil.remove(clientId);
    }
}
