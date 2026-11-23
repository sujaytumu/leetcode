package com.sujaytumu.leetcode.leaderboard;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.TestExecutorConfig;
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
class LeaderboardApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    @Test
    void pointsWeightHarderProblems() {
        org.junit.jupiter.api.Assertions.assertEquals(70, LeaderboardService.points(1, 1, 1));
    }

    @Test
    void rankedSolverAppearsWithOwnEntryAndNameFallback() throws Exception {
        String me = UUID.randomUUID().toString();
        String body = json.writeValueAsString(Map.of("language", "java", "code", TestExecutorConfig.SOLVE_TWO_SUM));
        mvc.perform(post("/api/problems/two-sum/submit").header(CLIENT, me)
                        .contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("ACCEPTED"));

        mvc.perform(get("/api/leaderboard?limit=5").header(CLIENT, me))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.participants").isNumber())
                .andExpect(jsonPath("$.me.you").value(true))
                .andExpect(jsonPath("$.me.easy").value(1))
                .andExpect(jsonPath("$.me.points").value(10))
                .andExpect(jsonPath("$.me.name").value("user-" + me.substring(0, 4)))
                .andExpect(jsonPath("$.me.rank").isNumber());

        // someone who never solved anything has no entry
        mvc.perform(get("/api/leaderboard").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.me").doesNotExist());
    }
}
