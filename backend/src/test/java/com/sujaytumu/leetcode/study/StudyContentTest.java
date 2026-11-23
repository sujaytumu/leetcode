package com.sujaytumu.leetcode.study;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.InputStream;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;

/** Guards the hand-written editorial data: no typos in slugs, nothing half-filled. */
class StudyContentTest {

    private static JsonNode read(String path) throws Exception {
        try (InputStream in = new ClassPathResource(path).getInputStream()) {
            return new ObjectMapper().readTree(in);
        }
    }

    @Test
    void everyEditorialBelongsToASeededProblemAndIsComplete() throws Exception {
        Set<String> slugs = new HashSet<>();
        read("seed/problems.json").forEach(p -> slugs.add(p.get("slug").asText()));
        read("seed/study.json").fields().forEachRemaining(e -> {
            assertTrue(slugs.contains(e.getKey()), "study entry for unknown problem " + e.getKey());
            JsonNode s = e.getValue();
            assertTrue(s.get("hints").size() >= 2, e.getKey() + " needs at least two hints");
            for (String f : new String[] {"approach", "time", "space"}) {
                assertFalse(s.get(f).asText().isBlank(), e.getKey() + " has an empty " + f);
            }
        });
    }
}
