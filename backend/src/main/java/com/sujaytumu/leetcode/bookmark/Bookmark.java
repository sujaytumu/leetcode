package com.sujaytumu.leetcode.bookmark;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(
        name = "bookmarks",
        uniqueConstraints = @UniqueConstraint(name = "uk_bookmark_client_problem", columnNames = {"client_id", "problem_id"}))
public class Bookmark {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Bookmark() {}

    public Bookmark(UUID clientId, Long problemId) {
        this.clientId = clientId;
        this.problemId = problemId;
    }

    public Long getId() {
        return id;
    }

    public UUID getClientId() {
        return clientId;
    }

    public Long getProblemId() {
        return problemId;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
