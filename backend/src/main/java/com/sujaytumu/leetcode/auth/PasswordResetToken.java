package com.sujaytumu.leetcode.auth;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;

/** A one-time password reset link. Only the SHA-256 of the token is stored, so a database leak cannot be used to reset. */
@Entity
@Table(
        name = "password_reset_tokens",
        uniqueConstraints = @UniqueConstraint(name = "uk_reset_token_hash", columnNames = "token_hash"))
public class PasswordResetToken {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "account_id", nullable = false)
    private Long accountId;

    @Column(name = "token_hash", length = 64, nullable = false)
    private String tokenHash;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    protected PasswordResetToken() {}

    public PasswordResetToken(Long accountId, String tokenHash, Instant expiresAt) {
        this.accountId = accountId;
        this.tokenHash = tokenHash;
        this.expiresAt = expiresAt;
    }

    public Long getId() { return id; }
    public Long getAccountId() { return accountId; }
    public String getTokenHash() { return tokenHash; }
    public Instant getExpiresAt() { return expiresAt; }
}
