package com.sujaytumu.leetcode.vote;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;
import java.util.UUID;

/** One client's like (+1) or dislike (-1) of a problem. */
@Entity
@Table(
        name = "problem_votes",
        uniqueConstraints = @UniqueConstraint(name = "uk_vote_client_problem", columnNames = {"client_id", "problem_id"}))
public class ProblemVote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(name = "vote_value", nullable = false)
    private int score;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected ProblemVote() {}

    public ProblemVote(UUID clientId, Long problemId, int score) {
        this.clientId = clientId;
        this.problemId = problemId;
        this.score = score;
    }

    public int getScore() {
        return score;
    }

    public void setScore(int score) {
        this.score = score;
        this.updatedAt = Instant.now();
    }
}
