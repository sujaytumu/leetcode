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

/** A client's private notes on one problem. */
@Entity
@Table(
        name = "problem_notes",
        uniqueConstraints = @UniqueConstraint(name = "uk_note_client_problem", columnNames = {"client_id", "problem_id"}))
public class ProblemNote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(nullable = false, length = 20000)
    private String content;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected ProblemNote() {}

    public ProblemNote(UUID clientId, Long problemId, String content) {
        this.clientId = clientId;
        this.problemId = problemId;
        this.content = content;
    }

    public String getContent() {
        return content;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setContent(String content) {
        this.content = content;
        this.updatedAt = Instant.now();
    }
}
