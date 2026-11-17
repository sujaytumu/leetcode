package com.sujaytumu.leetcode.lists;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.Instant;

@Entity
@Table(
        name = "problem_list_items",
        uniqueConstraints = @UniqueConstraint(name = "uk_list_problem", columnNames = {"list_id", "problem_id"}))
public class ProblemListItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "list_id", nullable = false)
    private Long listId;

    @Column(name = "problem_id", nullable = false)
    private Long problemId;

    @Column(name = "added_at", nullable = false)
    private Instant addedAt = Instant.now();

    protected ProblemListItem() {}

    public ProblemListItem(Long listId, Long problemId) {
        this.listId = listId;
        this.problemId = problemId;
    }

    public Long getId() {
        return id;
    }

    public Long getListId() {
        return listId;
    }

    public Long getProblemId() {
        return problemId;
    }
}
