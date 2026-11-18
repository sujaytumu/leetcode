package com.sujaytumu.leetcode.social;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileVisitRepository extends JpaRepository<ProfileVisit, Long> {

    boolean existsByProfileIdAndViewerIdAndDay(UUID profileId, UUID viewerId, LocalDate day);

    long countByProfileId(UUID profileId);

    long countByProfileIdAndCreatedAtAfter(UUID profileId, Instant since);
}
