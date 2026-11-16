package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.judge.Language;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(
        name = "submissions",
        indexes = @Index(name = "idx_submission_client_problem", columnList = "client_id, problem_id"))
public class Submission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Language language;

    @Column(nullable = false, length = 65536)
    private String code;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private Verdict verdict;

    @Column(name = "passed_count", nullable = false)
    private int passedCount;

    @Column(name = "total_count", nullable = false)
    private int totalCount;

    @Column(name = "runtime_ms")
    private Integer runtimeMs;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected Submission() {}

    public Submission(
            UUID clientId,
            Long problemId,
            Language language,
            String code,
            Verdict verdict,
            int passedCount,
            int totalCount,
            Integer runtimeMs) {
        this.clientId = clientId;
        this.problemId = problemId;
        this.language = language;
        this.code = code;
        this.verdict = verdict;
        this.passedCount = passedCount;
        this.totalCount = totalCount;
        this.runtimeMs = runtimeMs;
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

    public Language getLanguage() {
        return language;
    }

    public String getCode() {
        return code;
    }

    public Verdict getVerdict() {
        return verdict;
    }

    public int getPassedCount() {
        return passedCount;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public Integer getRuntimeMs() {
        return runtimeMs;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
