package com.sujaytumu.leetcode.problem;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

/** A stdin/stdout test. Sample cases are shown to users; the rest are hidden and only used on submit. */
@Entity
@Table(name = "test_cases")
public class TestCase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "problem_id")
    private Problem problem;

    @Column(nullable = false)
    private int position;

    @Column(nullable = false, length = 50000)
    private String input;

    @Column(name = "expected_output", nullable = false, length = 50000)
    private String expectedOutput;

    @Column(nullable = false)
    private boolean sample;

    protected TestCase() {}

    public TestCase(int position, String input, String expectedOutput, boolean sample) {
        this.position = position;
        this.input = input;
        this.expectedOutput = expectedOutput;
        this.sample = sample;
    }

    void setProblem(Problem problem) {
        this.problem = problem;
    }

    public Long getId() {
        return id;
    }

    public int getPosition() {
        return position;
    }

    public String getInput() {
        return input;
    }

    public String getExpectedOutput() {
        return expectedOutput;
    }

    public boolean isSample() {
        return sample;
    }
}
