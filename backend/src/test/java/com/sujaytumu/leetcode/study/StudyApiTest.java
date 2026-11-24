package com.sujaytumu.leetcode.study;

import static org.hamcrest.Matchers.hasItem;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import com.jayway.jsonpath.JsonPath;
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
    void returnsNoContentWhenThereIsNoStudyWriteUp() throws Exception {
        mvc.perform(get("/api/problems/no-such-problem/study")).andExpect(status().isNoContent());
    }

    @Test
    void buildsPlansFromTheCatalogue() throws Exception {
        mvc.perform(get("/api/plans"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("striver-sde"))
                .andExpect(jsonPath("$[0].total").value(62))
                .andExpect(jsonPath("$[?(@.id=='warmup')].total").value(hasItem(61)))
                .andExpect(jsonPath("$[?(@.id=='warmup')].solved").value(hasItem(0)))
                .andExpect(jsonPath("$[?(@.id=='hard')].total").value(hasItem(20)));
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
        int first = StudyService.dailyIndex(221, day);
        assertEquals(first, StudyService.dailyIndex(221, day));
        assertEquals(true, first >= 0 && first < 221);
    }

    @Test
    void dailyCalendarMatchesTheDailyPickAndStopsAtToday() throws Exception {
        String daily = mvc.perform(get("/api/daily").param("date", "2026-11-16"))
                .andReturn().getResponse().getContentAsString();
        String slug = JsonPath.read(daily, "$.problem.slug");

        mvc.perform(get("/api/daily/calendar").param("month", "2026-11").param("today", "2026-11-17"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.month").value("2026-11"))
                .andExpect(jsonPath("$.total").value(17))
                .andExpect(jsonPath("$.solved").value(0))
                .andExpect(jsonPath("$.days[0].date").value("2026-11-01"))
                .andExpect(jsonPath("$.days[15].date").value("2026-11-16"))
                .andExpect(jsonPath("$.days[15].problem.slug").value(slug));
    }

    @Test
    void dailyCalendarOfAPastMonthIsComplete() throws Exception {
        mvc.perform(get("/api/daily/calendar").param("month", "2026-02").param("today", "2026-11-17"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(28));
    }

    @Test
    void rejectsMalformedCalendarMonth() throws Exception {
        mvc.perform(get("/api/daily/calendar").param("month", "nov")).andExpect(status().isBadRequest());
    }
}
