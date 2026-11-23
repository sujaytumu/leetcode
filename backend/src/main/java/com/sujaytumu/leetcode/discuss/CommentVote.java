package com.sujaytumu.leetcode.discuss;

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
        name = "comment_votes",
        uniqueConstraints = @UniqueConstraint(name = "uk_comment_vote", columnNames = {"comment_id", "client_id"}))
public class CommentVote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "comment_id", nullable = false)
    private Long commentId;

    @Column(name = "client_id", nullable = false)
    private UUID clientId;

    /** Nullable: votes cast before this column existed have no time. */
    @Column(name = "created_at")
    private Instant createdAt = Instant.now();

    protected CommentVote() {}

    public CommentVote(Long commentId, UUID clientId) {
        this.commentId = commentId;
        this.clientId = clientId;
    }
}
