package com.sujaytumu.leetcode.auth;

import java.time.Instant;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PasswordResetTokenRepository extends JpaRepository<PasswordResetToken, Long> {

    Optional<PasswordResetToken> findByTokenHash(String tokenHash);

    long deleteByAccountId(Long accountId);

    long deleteByExpiresAtBefore(Instant cutoff);
}
