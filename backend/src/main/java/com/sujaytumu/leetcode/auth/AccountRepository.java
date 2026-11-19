package com.sujaytumu.leetcode.auth;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

public interface AccountRepository extends JpaRepository<Account, Long> {

    Optional<Account> findByUsername(String username);

    Optional<Account> findByClientId(UUID clientId);

    Optional<Account> findByEmail(String email);

    boolean existsByEmail(String email);

    boolean existsByUsername(String username);

    boolean existsByClientId(UUID clientId);

    List<Account> findByDailyEmailTrue();

    /** Targeted update so a long mailing run never overwrites a password change made meanwhile. */
    @Transactional
    @Modifying
    @Query("update Account a set a.lastDailySent = :day where a.id = :id")
    int markDailySent(@Param("id") Long id, @Param("day") LocalDate day);
}
