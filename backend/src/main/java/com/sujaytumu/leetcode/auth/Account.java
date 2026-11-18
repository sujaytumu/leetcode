package com.sujaytumu.leetcode.auth;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

/**
 * A registered account. All progress is still keyed by {@code clientId}; the account simply owns one, so
 * registering from a browser keeps everything that browser already did, and logging in elsewhere restores it.
 */
@Entity
@Table(
        name = "accounts",
        uniqueConstraints = {
            @UniqueConstraint(name = "uk_accounts_username", columnNames = "username"),
            @UniqueConstraint(name = "uk_accounts_email", columnNames = "email"),
            @UniqueConstraint(name = "uk_accounts_client", columnNames = "client_id")
        })
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Lower-cased for lookups. */
    @Column(name = "username", length = 20, nullable = false)
    private String username;

    /** Lower-cased; null only for accounts created before email sign-up existed. */
    @Column(name = "email", length = 254)
    private String email;

    @Column(name = "password_hash", length = 200, nullable = false)
    private String passwordHash;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    /** Bumped on password change; tokens carry it so old tokens stop working. */
    @Column(name = "token_version", nullable = false)
    private int tokenVersion = 0;

    protected Account() {}

    public Account(String username, String passwordHash, UUID clientId) {
        this.username = username;
        this.passwordHash = passwordHash;
        this.clientId = clientId;
    }

    public Account(String email, String username, String passwordHash, UUID clientId) {
        this(username, passwordHash, clientId);
        this.email = email;
    }

    public String getEmail() { return email; }
    public Long getId() { return id; }
    public String getUsername() { return username; }
    public String getPasswordHash() { return passwordHash; }
    public UUID getClientId() { return clientId; }
    public Instant getCreatedAt() { return createdAt; }
    public int getTokenVersion() { return tokenVersion; }

    public void changePassword(String newHash) {
        this.passwordHash = newHash;
        this.tokenVersion++;
    }
}
