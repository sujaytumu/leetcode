package com.sujaytumu.leetcode.discuss;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/** A discussion comment on a problem. Replies point at a top-level comment through {@code parentId}. */
@Entity
@Table(name = "comments", indexes = @Index(name = "idx_comments_problem", columnList = "problem_id"))
public class Comment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "parent_id")
    private Long parentId;

    @Column(nullable = false, length = 60)
    private String author;

    @Column(nullable = false, length = 2000)
    private String body;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Comment() {}

    public Comment(Long problemId, UUID clientId, Long parentId, String author, String body) {
        this.problemId = problemId;
        this.clientId = clientId;
        this.parentId = parentId;
        this.author = author;
        this.body = body;
    }

    public Long getId() { return id; }
    public Long getProblemId() { return problemId; }
    public UUID getClientId() { return clientId; }
    public Long getParentId() { return parentId; }
    public String getAuthor() { return author; }
    public String getBody() { return body; }
    public Instant getCreatedAt() { return createdAt; }
}
