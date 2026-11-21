package com.sujaytumu.leetcode.solution;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.Optional;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

/**
 * Reference answers (classpath:seed/solutions.json, built from the verified files under problems/ by
 * scripts/build-solutions.js). They are only returned on request, so the UI can keep them behind a click.
 */
@Service
public class SolutionService {

    /** {@code solutions} maps a language key (python, java, cpp, javascript) to the optimised source code;
     *  {@code bruteForce} (optional, may be null) maps a language key to the naive version of the same problem. */
    public record Answer(String editorial, Map<String, String> solutions, Map<String, String> bruteForce) {}

    private final Map<String, Answer> answers;

    public SolutionService(ObjectMapper objectMapper) throws IOException {
        ClassPathResource resource = new ClassPathResource("seed/solutions.json");
        if (!resource.exists()) {
            this.answers = Map.of();
            return;
        }
        try (InputStream in = resource.getInputStream()) {
            this.answers = objectMapper.readValue(in, new TypeReference<Map<String, Answer>>() {});
        }
    }

    public Optional<Answer> answer(String slug) {
        return Optional.ofNullable(answers.get(slug));
    }
}
