package com.sujaytumu.leetcode.auth;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AccountRepository extends JpaRepository<Account, Long> {

    Optional<Account> findByUsername(String username);

    Optional<Account> findByClientId(UUID clientId);

    boolean existsByUsername(String username);

    boolean existsByClientId(UUID clientId);
}
