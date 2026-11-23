package com.sujaytumu.leetcode.study;

import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.is;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.TestExecutorConfig;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class RecommendationApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    @Test
    void newClientGetsEasyProblemsToStartWith() throws Exception {
        mvc.perform(get("/api/recommendations").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.next.length()").value(6))
                .andExpect(jsonPath("$.next[*].problem.difficulty", everyItem(is("EASY"))))
                .andExpect(jsonPath("$.unfinished.length()").value(0))
                .andExpect(jsonPath("$.revisit.length()").value(0));
    }

    @Test
    void solvedProblemIsNotRecommendedAgainAndNotYetDueForRevisit() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(post("/api/problems/two-sum/submit")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(
                                Map.of("language", "python", "code", TestExecutorConfig.SOLVE_TWO_SUM))))
                .andExpect(status().isOk());

        mvc.perform(get("/api/recommendations").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.next[*].problem.slug", not(hasItem("two-sum"))))
                .andExpect(jsonPath("$.revisit.length()").value(0));
    }

    @Test
    void countsWholeDaysSinceASolve() {
        Instant now = Instant.parse("2026-11-17T12:00:00Z");
        assertEquals(10, RecommendationService.daysSince(Instant.parse("2026-11-07T12:00:00Z"), now));
        assertEquals(0, RecommendationService.daysSince(Instant.parse("2026-11-17T01:00:00Z"), now));
    }
}
