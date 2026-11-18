package com.sujaytumu.leetcode.social;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

/** {@code followerId} follows {@code followeeId}; both are client ids. */
@Entity
@Table(
        name = "follows",
        uniqueConstraints = @UniqueConstraint(name = "uk_follow", columnNames = {"follower_id", "followee_id"}))
public class Follow {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "follower_id", nullable = false)
    private UUID followerId;

    @Column(name = "followee_id", nullable = false)
    private UUID followeeId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Follow() {}

    public Follow(UUID followerId, UUID followeeId) {
        this.followerId = followerId;
        this.followeeId = followeeId;
    }
}
