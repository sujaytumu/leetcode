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
 * so it is safe to run against a populated database and never overwrites edited content.
 * The file is produced by backend/tools/generate_seed.py.
 */
@Component
public class DataSeeder implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DataSeeder.class);

    record SeedTestCase(String input, String expectedOutput, boolean sample) {}

    record SeedProblem(
            String slug,
            String title,
            Difficulty difficulty,
            List<String> tags,
            String description,
            Map<String, String> starterCode,
            List<SeedTestCase> testCases) {}

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
            if (problems.findBySlug(item.slug()).isPresent()) {
                continue;
            }
            Problem problem = new Problem(item.slug(), item.title(), item.difficulty(), item.description());
            problem.setTags(new LinkedHashSet<>(item.tags()));
            problem.setStarterCode(item.starterCode());
            for (int i = 0; i < item.testCases().size(); i++) {
                SeedTestCase tc = item.testCases().get(i);
                problem.addTestCase(new TestCase(i, tc.input(), tc.expectedOutput(), tc.sample()));
            }
            problems.save(problem);
            inserted++;
        }
        log.info("Seeded {} new problem(s); {} total", inserted, problems.count());
    }
}
