package com.sujaytumu.leetcode.study;

import static org.hamcrest.Matchers.hasItem;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.sujaytumu.leetcode.TestExecutorConfig;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class StudyApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void servesStudyContentFromTheBackend() throws Exception {
        mvc.perform(get("/api/problems/two-sum/study"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.hints.length()").value(3))
                .andExpect(jsonPath("$.time").value("O(n)"))
                .andExpect(jsonPath("$.approach").isNotEmpty());
    }

    @Test
    void returnsNoContentWhenAProblemHasNoStudyWriteUp() throws Exception {
        mvc.perform(get("/api/problems/find-if-path-exists-in-graph/study")).andExpect(status().isNoContent());
    }

    @Test
    void buildsPlansFromTheCatalogue() throws Exception {
        mvc.perform(get("/api/plans"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("warmup"))
                .andExpect(jsonPath("$[0].total").value(43))
                .andExpect(jsonPath("$[0].solved").value(0))
                .andExpect(jsonPath("$[0].problems.length()").value(43))
                .andExpect(jsonPath("$[?(@.id=='hard')].total").value(hasItem(11)));
    }

    @Test
    void picksTheSameDailyProblemForTheSameDay() throws Exception {
        mvc.perform(get("/api/daily").param("date", "2026-11-16"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.date").value("2026-11-16"))
                .andExpect(jsonPath("$.problem.slug").isNotEmpty());
    }

    @Test
    void rejectsMalformedDailyDate() throws Exception {
        mvc.perform(get("/api/daily").param("date", "tomorrow")).andExpect(status().isBadRequest());
    }

    @Test
    void dailyIndexIsDeterministicAndInRange() {
        LocalDate day = LocalDate.of(2026, 11, 16);
        int first = StudyService.dailyIndex(122, day);
        assertEquals(first, StudyService.dailyIndex(122, day));
        assertEquals(true, first >= 0 && first < 122);
    }
}
