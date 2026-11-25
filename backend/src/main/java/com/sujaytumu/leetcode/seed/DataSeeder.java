package com.sujaytumu.leetcode.seed;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.config.AppProperties;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.problem.TestCase;
import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * Loads classpath:seed/problems.json on startup. Only inserts problems whose slug does not exist yet,
 * so it is safe to run against a populated database and never overwrites edited content (only the study-path
 * position, {@code order}, is refreshed on existing rows).
 * The file is produced by backend/tools/generate_seed.py.
 */
@Component
public class DataSeeder implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DataSeeder.class);

    /** The test_cases columns hold 50,000 characters; a longer value aborts the whole seed (and the server start). */
    private static final int MAX_CASE_CHARS = 50_000;

    record SeedTestCase(String input, String expectedOutput, boolean sample) {}

    record SeedProblem(
            String slug,
            String title,
            Difficulty difficulty,
            List<String> tags,
            String description,
            Map<String, String> starterCode,
            List<SeedTestCase> testCases,
            Integer order) {}

    private final ProblemRepository problems;
    private final ObjectMapper objectMapper;
    private final AppProperties properties;

    public DataSeeder(ProblemRepository problems, ObjectMapper objectMapper, AppProperties properties) {
        this.problems = problems;
        this.objectMapper = objectMapper;
        this.properties = properties;
    }

    @Override
    @Transactional
    public void run(ApplicationArguments args) throws IOException {
        if (!properties.seed().enabled()) {
            log.info("Seeding disabled");
            return;
        }

        List<SeedProblem> seed;
        try (InputStream in = new ClassPathResource("seed/problems.json").getInputStream()) {
            seed = objectMapper.readValue(in, new TypeReference<>() {});
        }

        int inserted = 0;
        for (SeedProblem item : seed) {
            Problem existing = problems.findBySlug(item.slug()).orElse(null);
            if (existing != null) {
                // Content is never overwritten, but the study-path position is kept in step with the seed file.
                if (item.order() != null && !item.order().equals(existing.getSortOrder())) {
                    existing.setSortOrder(item.order());
                }
                continue;
            }
            Problem problem = new Problem(item.slug(), item.title(), item.difficulty(), item.description());
            problem.setTags(new LinkedHashSet<>(item.tags()));
            problem.setStarterCode(item.starterCode());
            problem.setSortOrder(item.order());
            int position = 0;
            for (SeedTestCase tc : item.testCases()) {
                if (tc.input().length() > MAX_CASE_CHARS || tc.expectedOutput().length() > MAX_CASE_CHARS) {
                    log.warn("Skipping an oversized test case of {} (input {} / output {} chars)", item.slug(),
                            tc.input().length(), tc.expectedOutput().length());
                    continue;
                }
                problem.addTestCase(new TestCase(position++, tc.input(), tc.expectedOutput(), tc.sample()));
            }
            problems.save(problem);
            inserted++;
        }
        log.info("Seeded {} new problem(s); {} total", inserted, problems.count());
    }
}
