package com.sujaytumu.leetcode.profileinfo;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileInfoRepository extends JpaRepository<ProfileInfo, UUID> {}
