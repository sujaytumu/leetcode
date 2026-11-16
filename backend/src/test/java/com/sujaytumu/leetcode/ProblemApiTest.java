package com.sujaytumu.leetcode;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
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
class ProblemApiTest {

    @Autowired
    MockMvc mvc;

    @Test
    void listsSeededProblemsWithPaging() throws Exception {
        mvc.perform(get("/api/problems").param("size", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(122))
                .andExpect(jsonPath("$.totalPages").value(25))
                .andExpect(jsonPath("$.items.length()").value(5))
                .andExpect(jsonPath("$.items[0].slug").value("two-sum"))
                .andExpect(jsonPath("$.items[0].status").value("TODO"));
    }

    @Test
    void clampsOversizedPageSize() throws Exception {
        mvc.perform(get("/api/problems").param("size", "100000"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.size").value(100));
    }

    @Test
    void filtersByDifficultyCaseInsensitively() throws Exception {
        mvc.perform(get("/api/problems").param("difficulty", "hard"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(9));
    }

    @Test
    void filtersByTag() throws Exception {
        mvc.perform(get("/api/problems").param("tag", "dynamic-programming"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(28))
                .andExpect(jsonPath("$.items[*].slug").value(hasItem("coin-change")));
    }

    @Test
    void searchesTitleAndSlugAndTreatsWildcardsLiterally() throws Exception {
        mvc.perform(get("/api/problems").param("q", "SUM"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(9))
                .andExpect(jsonPath("$.items[0].slug").value("two-sum"));

        mvc.perform(get("/api/problems").param("q", "%"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements").value(0));
    }

    @Test
    void combinesFilters() throws Exception {
        mvc.perform(get("/api/problems").param("difficulty", "easy").param("tag", "array"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[*].slug").value(hasItem("two-sum")))
                .andExpect(jsonPath("$.items[*].slug").value(not(hasItem("coin-change"))));
    }

    @Test
    void detailExposesOnlySamplesAndStarterCode() throws Exception {
        mvc.perform(get("/api/problems/two-sum"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Two Sum"))
                .andExpect(jsonPath("$.samples.length()").value(2))
                .andExpect(jsonPath("$.samples[0].input").value("4\n2 7 11 15\n9\n"))
                .andExpect(jsonPath("$.samples[0].expectedOutput").value("0 1\n"))
                .andExpect(jsonPath("$.starterCode.java").value(containsString("public class Main")))
                .andExpect(jsonPath("$.starterCode.python").exists())
                .andExpect(jsonPath("$.starterCode.javascript").exists())
                .andExpect(jsonPath("$.starterCode.cpp").exists())
                .andExpect(content().string(not(containsString("testCases"))));
    }

    @Test
    void unknownProblemIs404() throws Exception {
        mvc.perform(get("/api/problems/does-not-exist"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.detail").value("Problem not found: does-not-exist"));
    }

    @Test
    void rejectsBadFilterValues() throws Exception {
        mvc.perform(get("/api/problems").param("difficulty", "impossible")).andExpect(status().isBadRequest());
        mvc.perform(get("/api/problems").param("status", "nope")).andExpect(status().isBadRequest());
    }

    @Test
    void statusAndBookmarkFiltersNeedClientId() throws Exception {
        mvc.perform(get("/api/problems").param("status", "solved")).andExpect(status().isBadRequest());
        mvc.perform(get("/api/problems").param("bookmarked", "true")).andExpect(status().isBadRequest());
    }

    @Test
    void listsDistinctSortedTags() throws Exception {
        mvc.perform(get("/api/tags"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0]").value("array"))
                .andExpect(jsonPath("$").value(hasItem("two-pointers")));
    }
}
