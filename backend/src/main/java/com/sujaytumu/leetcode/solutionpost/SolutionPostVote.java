package com.sujaytumu.leetcode.solutionpost;

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
        name = "solution_post_votes",
        uniqueConstraints = @UniqueConstraint(name = "uk_solution_post_vote", columnNames = {"post_id", "client_id"}))
public class SolutionPostVote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "post_id", nullable = false)
    private Long postId;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    @Column(name = "created_at")
    private Instant createdAt = Instant.now();

    protected SolutionPostVote() {}

    public SolutionPostVote(Long postId, UUID clientId) {
        this.postId = postId;
        this.clientId = clientId;
    }
}
