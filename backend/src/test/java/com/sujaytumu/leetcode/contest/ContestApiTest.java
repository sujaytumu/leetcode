package com.sujaytumu.leetcode.contest;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.sujaytumu.leetcode.TestExecutorConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class ContestApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void overviewListsTheCurrentContestAndFinishedOnes() throws Exception {
        mvc.perform(get("/api/contests"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.current.title").isString())
                .andExpect(jsonPath("$.current.state").isString())
                .andExpect(jsonPath("$.past", hasSize(8)))
                .andExpect(jsonPath("$.past[0].state").value("FINISHED"))
                .andExpect(jsonPath("$.past[0].problems", hasSize(4)))
                .andExpect(jsonPath("$.past[0].problems[0].points").value(3))
                .andExpect(jsonPath("$.past[0].problems[3].points").value(6));
    }

    @Test
    void finishedContestHasStandingsAndFutureOnesDoNotExist() throws Exception {
        mvc.perform(get("/api/contests/0"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.contest.id").value(0))
                .andExpect(jsonPath("$.contest.state").value("FINISHED"))
                .andExpect(jsonPath("$.participants").value(0))
                .andExpect(jsonPath("$.rows", hasSize(0)));
        mvc.perform(get("/api/contests/99999")).andExpect(status().isNotFound());
        mvc.perform(get("/api/contests/-1")).andExpect(status().isNotFound());
    }
}
