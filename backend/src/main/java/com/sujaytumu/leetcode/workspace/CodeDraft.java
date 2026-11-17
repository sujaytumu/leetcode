package com.sujaytumu.leetcode.workspace;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

/** A client's unsubmitted code for one problem in one language, so work follows them across devices. */
@Entity
@Table(
        name = "code_drafts",
        uniqueConstraints = @UniqueConstraint(
                name = "uk_draft_client_problem_language",
                columnNames = {"client_id", "problem_id", "language"}))
public class CodeDraft {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(nullable = false, length = 20)
    private String language;

    @Column(nullable = false, length = 65536)
    private String code;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected CodeDraft() {}

    public CodeDraft(UUID clientId, Long problemId, String language, String code) {
        this.clientId = clientId;
        this.problemId = problemId;
        this.language = language;
        this.code = code;
    }

    public String getLanguage() {
        return language;
    }

    public String getCode() {
        return code;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setCode(String code) {
        this.code = code;
        this.updatedAt = Instant.now();
    }
}
