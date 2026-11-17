package com.sujaytumu.leetcode;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class SolutionApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void returnsAnswersInSeveralLanguagesWhenPublished() throws Exception {
        mvc.perform(get("/api/problems/two-sum/solution"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.solutions.python").value(containsString("class Solution")))
                .andExpect(jsonPath("$.solutions.java").exists())
                .andExpect(jsonPath("$.solutions.cpp").exists());
    }

    @Test
    void returnsNoContentWhenNoAnswerIsPublished() throws Exception {
        mvc.perform(get("/api/problems/no-such-problem/solution")).andExpect(status().isNoContent());
    }
}
