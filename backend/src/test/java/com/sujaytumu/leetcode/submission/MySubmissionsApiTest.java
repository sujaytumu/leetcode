package com.sujaytumu.leetcode.submission;

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
class MySubmissionsApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private void submit(String client, String slug, String code) throws Exception {
        mvc.perform(post("/api/problems/" + slug + "/submit").header(CLIENT, client)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of("language", "python", "code", code))))
                .andExpect(status().isOk());
    }

    @Test
    void listsOwnSubmissionsNewestFirstAndFiltersByVerdict() throws Exception {
        String me = UUID.randomUUID().toString();
        submit(me, "two-sum", TestExecutorConfig.WRONG_ANSWER);
        submit(me, "two-sum", TestExecutorConfig.SOLVE_TWO_SUM);
        submit(UUID.randomUUID().toString(), "two-sum", TestExecutorConfig.SOLVE_TWO_SUM); // someone else's

        mvc.perform(get("/api/submissions").header(CLIENT, me))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(2))
                .andExpect(jsonPath("$.items[0].verdict").value("ACCEPTED"))
                .andExpect(jsonPath("$.items[0].slug").value("two-sum"))
                .andExpect(jsonPath("$.items[0].title").value("Two Sum"))
                .andExpect(jsonPath("$.items[1].verdict").value("WRONG_ANSWER"));

        mvc.perform(get("/api/submissions?verdict=WRONG_ANSWER").header(CLIENT, me))
                .andExpect(jsonPath("$.totalElements").value(1))
                .andExpect(jsonPath("$.items[0].verdict").value("WRONG_ANSWER"));

        mvc.perform(get("/api/submissions").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(jsonPath("$.totalElements").value(0));
    }
}
