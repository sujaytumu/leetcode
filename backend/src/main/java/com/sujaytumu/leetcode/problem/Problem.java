package com.sujaytumu.leetcode.problem;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.hibernate.annotations.BatchSize;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "problems")
public class Problem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 120)
    private String slug;

    @Column(nullable = false, length = 200)
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Difficulty difficulty;

    @Column(nullable = false, length = 20000)
    private String description;

    /** Language key (java, python, javascript, cpp) to starter source. */
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, String> starterCode = new HashMap<>();

    @ElementCollection
    @CollectionTable(name = "problem_tags", joinColumns = @JoinColumn(name = "problem_id"))
    @Column(name = "tag", nullable = false, length = 50)
    @BatchSize(size = 50)
    private Set<String> tags = new LinkedHashSet<>();

    @OneToMany(mappedBy = "problem", cascade = jakarta.persistence.CascadeType.ALL, orphanRemoval = true)
    @OrderBy("position ASC")
    private List<TestCase> testCases = new ArrayList<>();

    protected Problem() {}

    public Problem(String slug, String title, Difficulty difficulty, String description) {
        this.slug = slug;
        this.title = title;
        this.difficulty = difficulty;
        this.description = description;
    }

    public void addTestCase(TestCase testCase) {
        testCase.setProblem(this);
        testCases.add(testCase);
    }

    public Long getId() {
        return id;
    }

    public String getSlug() {
        return slug;
    }

    public String getTitle() {
        return title;
    }

    public Difficulty getDifficulty() {
        return difficulty;
    }

    public String getDescription() {
        return description;
    }

    public Map<String, String> getStarterCode() {
        return starterCode;
    }

    public void setStarterCode(Map<String, String> starterCode) {
        this.starterCode = starterCode;
    }

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags;
    }

    public List<TestCase> getTestCases() {
        return testCases;
    }
}
