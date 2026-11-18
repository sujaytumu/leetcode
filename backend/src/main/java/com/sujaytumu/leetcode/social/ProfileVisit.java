package com.sujaytumu.leetcode.social;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

/** One viewer looking at one profile on one (UTC) day, so refreshing the page does not inflate Views. */
@Entity
@Table(
        name = "profile_visits",
        uniqueConstraints = @UniqueConstraint(name = "uk_profile_visit", columnNames = {"profile_id", "viewer_id", "day"}))
public class ProfileVisit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "profile_id", nullable = false)
    private UUID profileId;

    @Column(name = "viewer_id", nullable = false)
    private UUID viewerId;

    @Column(name = "day", nullable = false)
    private LocalDate day;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected ProfileVisit() {}

    public ProfileVisit(UUID profileId, UUID viewerId, LocalDate day) {
        this.profileId = profileId;
        this.viewerId = viewerId;
        this.day = day;
    }
}
