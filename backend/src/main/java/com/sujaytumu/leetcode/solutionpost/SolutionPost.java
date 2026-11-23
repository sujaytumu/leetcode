package com.sujaytumu.leetcode.solutionpost;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/** A community-written solution to a problem (LeetCode's "Solutions" tab). Body is Markdown. */
@Entity
@Table(name = "solution_posts", indexes = @Index(name = "idx_solution_posts_problem", columnList = "problem_id"))
public class SolutionPost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(nullable = false, length = 60)
    private String author;

    @Column(nullable = false, length = 120)
    private String title;

    @Column(nullable = false, length = 20000)
    private String body;

    @Column(length = 20)
    private String language;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected SolutionPost() {}

    public SolutionPost(Long problemId, UUID clientId, String author, String title, String body, String language) {
        this.problemId = problemId;
        this.clientId = clientId;
        this.author = author;
        this.title = title;
        this.body = body;
        this.language = language;
    }

    public void edit(String title, String body, String language) {
        this.title = title;
        this.body = body;
        this.language = language;
        this.updatedAt = Instant.now();
    }

    public Long getId() { return id; }
    public Long getProblemId() { return problemId; }
    public UUID getClientId() { return clientId; }
    public String getAuthor() { return author; }
    public String getTitle() { return title; }
    public String getBody() { return body; }
    public String getLanguage() { return language; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
