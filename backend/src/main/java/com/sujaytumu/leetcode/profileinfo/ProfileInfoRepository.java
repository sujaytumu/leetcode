package com.sujaytumu.leetcode.profileinfo;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileInfoRepository extends JpaRepository<ProfileInfo, UUID> {

    Optional<ProfileInfo> findFirstByUsernameIgnoreCase(String username);

    boolean existsByUsernameIgnoreCaseAndClientIdNot(String username, UUID clientId);
}
