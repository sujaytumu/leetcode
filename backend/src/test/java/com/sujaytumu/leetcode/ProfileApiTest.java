package com.sujaytumu.leetcode;

import static org.hamcrest.Matchers.hasItem;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
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
class ProfileApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    @Test
    void newClientHasNoContestRatingYet() throws Exception {
        mvc.perform(get("/api/profile/rating").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.attended").value(0))
                .andExpect(jsonPath("$.history.length()").value(0));
    }

    @Test
    void newClientHasAnEmptyProfile() throws Exception {
        mvc.perform(get("/api/profile").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.progress.total").value(221))
                .andExpect(jsonPath("$.progress.solved").value(0))
                .andExpect(jsonPath("$.attempting").value(0))
                .andExpect(jsonPath("$.submissionsPastYear").value(0))
                .andExpect(jsonPath("$.activeDays").value(0))
                .andExpect(jsonPath("$.currentStreak").value(0))
                .andExpect(jsonPath("$.calendar.length()").value(0))
                .andExpect(jsonPath("$.recentAccepted.length()").value(0))
                .andExpect(jsonPath("$.community.discuss").value(0))
                .andExpect(jsonPath("$.community.reputation").value(0));
    }

    @Test
    void acceptedSubmissionShowsUpInEveryProfileSection() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(post("/api/problems/two-sum/submit")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(
                                Map.of("language", "python", "code", TestExecutorConfig.SOLVE_TWO_SUM))))
                .andExpect(status().isOk());

        mvc.perform(get("/api/profile").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.progress.solved").value(1))
                .andExpect(jsonPath("$.progress.byDifficulty.EASY.solved").value(1))
                .andExpect(jsonPath("$.submissionsPastYear").value(1))
                .andExpect(jsonPath("$.activeDays").value(1))
                .andExpect(jsonPath("$.maxStreak").value(1))
                .andExpect(jsonPath("$.currentStreak").value(1))
                .andExpect(jsonPath("$.calendar[0].count").value(1))
                .andExpect(jsonPath("$.recentAccepted[0].slug").value("two-sum"))
                .andExpect(jsonPath("$.recentAccepted[0].language").value("python"))
                .andExpect(jsonPath("$.skills[*].tag").value(hasItem("array")))
                .andExpect(jsonPath("$.languages[0].language").value("python"))
                .andExpect(jsonPath("$.languages[0].solved").value(1))
                .andExpect(jsonPath("$.badges.length()").value(15))
                .andExpect(jsonPath("$.badges[?(@.id=='solved-1')].earned").value(hasItem(true)))
                .andExpect(jsonPath("$.badges[?(@.id=='solved-10')].earned").value(hasItem(false)));
    }

    @Test
    void rejectsUnknownTimeZone() throws Exception {
        mvc.perform(get("/api/profile").param("zone", "Mars/Olympus").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isBadRequest());
    }
}
