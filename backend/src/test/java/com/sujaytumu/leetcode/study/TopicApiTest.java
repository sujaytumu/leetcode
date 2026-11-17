package com.sujaytumu.leetcode.study;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
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
class TopicApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void listsTopicsWithCountsBiggestFirst() throws Exception {
        mvc.perform(get("/api/topics"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].total", greaterThan(0)))
                .andExpect(jsonPath("$[0].solved").value(0))
                .andExpect(jsonPath("$[*].tag").value(hasItem("array")))
                .andExpect(jsonPath("$[0].byDifficulty.EASY", greaterThan(-1)))
                .andExpect(jsonPath("$[0].byDifficulty.HARD", greaterThan(-1)));
    }
}
