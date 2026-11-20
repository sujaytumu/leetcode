package com.sujaytumu.leetcode;

import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
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
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class SubmissionApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private MockHttpServletRequestBuilder judge(String action, UUID client, String language, String code)
            throws Exception {
        return post("/api/problems/two-sum/" + action)
                .header(CLIENT, client.toString())
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(Map.of("language", language, "code", code)));
    }

    @Test
    void runWithCorrectCodePassesSamplesAndIsNotPersisted() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(judge("run", client, "python", TestExecutorConfig.SOLVE_TWO_SUM))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("ACCEPTED"))
                .andExpect(jsonPath("$.passed").value(2))
                .andExpect(jsonPath("$.total").value(2))
                .andExpect(jsonPath("$.submissionId").value(nullValue()));

        mvc.perform(get("/api/problems/two-sum/submissions").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void acceptedSubmissionRecordsMemoryAndServesStatsOnlyToItsOwner() throws Exception {
        UUID client = UUID.randomUUID();
        String body = mvc.perform(judge("submit", client, "java", TestExecutorConfig.SOLVE_TWO_SUM))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.runtimeMs").value(20))
                .andExpect(jsonPath("$.memoryKb").value(2048))
                .andReturn().getResponse().getContentAsString();
        long id = json.readTree(body).get("submissionId").asLong();

        mvc.perform(get("/api/problems/two-sum/submissions").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$[0].memoryKb").value(2048));

        mvc.perform(get("/api/submissions/" + id + "/stats").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.submissionId").value(id))
                .andExpect(jsonPath("$.runtime.value").value(20))
                .andExpect(jsonPath("$.memory.value").value(2048))
                .andExpect(jsonPath("$.runtime.bins").isArray());

        mvc.perform(get("/api/submissions/" + id + "/stats").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isNotFound());
    }

    @Test
    void submitCorrectCodeRunsAllCasesAndMarksSolved() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(judge("submit", client, "java", TestExecutorConfig.SOLVE_TWO_SUM))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("ACCEPTED"))
                .andExpect(jsonPath("$.passed").value(9))
                .andExpect(jsonPath("$.total").value(9))
                .andExpect(jsonPath("$.submissionId").isNumber())
                .andExpect(jsonPath("$.cases[8].sample").value(false))
                // hidden cases never leak their data
                .andExpect(jsonPath("$.cases[8].input").value(nullValue()))
                .andExpect(jsonPath("$.cases[8].expected").value(nullValue()));

        mvc.perform(get("/api/problems/two-sum").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.status").value("SOLVED"));

        mvc.perform(get("/api/problems").param("status", "solved").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(1))
                .andExpect(jsonPath("$.items[0].slug").value("two-sum"));

        mvc.perform(get("/api/problems").param("status", "todo").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(204));

        mvc.perform(get("/api/progress").header(CLIENT, client.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(205))
                .andExpect(jsonPath("$.solved").value(1))
                .andExpect(jsonPath("$.attempted").value(1))
                .andExpect(jsonPath("$.byDifficulty.EASY.total").value(61))
                .andExpect(jsonPath("$.byDifficulty.EASY.solved").value(1))
                .andExpect(jsonPath("$.byDifficulty.HARD.solved").value(0));
    }

    @Test
    void wrongAnswerStopsAtFirstFailureAndMarksAttempted() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(judge("submit", client, "python", TestExecutorConfig.WRONG_ANSWER))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("WRONG_ANSWER"))
                .andExpect(jsonPath("$.passed").value(0))
                .andExpect(jsonPath("$.total").value(9))
                .andExpect(jsonPath("$.cases.length()").value(1))
                .andExpect(jsonPath("$.message").value("Wrong answer on sample case 1."))
                .andExpect(jsonPath("$.cases[0].actual").value("9 9\n"))
                .andExpect(jsonPath("$.cases[0].expected").value("0 1\n"));

        mvc.perform(get("/api/problems").param("status", "attempted").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(1));
        mvc.perform(get("/api/problems").param("status", "solved").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(0));
    }

    @Test
    void reportsCompileRuntimeAndTimeLimitVerdicts() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(judge("run", client, "cpp", TestExecutorConfig.COMPILE_ERROR))
                .andExpect(jsonPath("$.verdict").value("COMPILE_ERROR"))
                .andExpect(jsonPath("$.message").value("Compilation failed."))
                .andExpect(jsonPath("$.cases[0].error").value(containsString("expected")));

        mvc.perform(judge("run", client, "python", TestExecutorConfig.RUNTIME_ERROR))
                .andExpect(jsonPath("$.verdict").value("RUNTIME_ERROR"))
                .andExpect(jsonPath("$.cases[0].error").value(containsString("IndexError")));

        mvc.perform(judge("run", client, "javascript", TestExecutorConfig.TIME_LIMIT))
                .andExpect(jsonPath("$.verdict").value("TIME_LIMIT_EXCEEDED"));
    }

    @Test
    void historyListsNewestFirstWithCode() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(judge("submit", client, "python", TestExecutorConfig.WRONG_ANSWER)).andExpect(status().isOk());
        mvc.perform(judge("submit", client, "python", TestExecutorConfig.SOLVE_TWO_SUM)).andExpect(status().isOk());

        mvc.perform(get("/api/problems/two-sum/submissions").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].verdict").value("ACCEPTED"))
                .andExpect(jsonPath("$[1].verdict").value("WRONG_ANSWER"))
                .andExpect(jsonPath("$[0].language").value("python"))
                .andExpect(jsonPath("$[0].code").value(TestExecutorConfig.SOLVE_TWO_SUM));
    }

    @Test
    void progressIsIsolatedPerClient() throws Exception {
        UUID solver = UUID.randomUUID();
        UUID other = UUID.randomUUID();
        mvc.perform(judge("submit", solver, "python", TestExecutorConfig.SOLVE_TWO_SUM)).andExpect(status().isOk());

        mvc.perform(get("/api/progress").header(CLIENT, other.toString()))
                .andExpect(jsonPath("$.solved").value(0))
                .andExpect(jsonPath("$.attempted").value(0));
    }

    @Test
    void bookmarksAreIdempotentAndFilterable() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(put("/api/problems/coin-change/bookmark").header(CLIENT, client.toString()))
                .andExpect(status().isNoContent());
        mvc.perform(put("/api/problems/coin-change/bookmark").header(CLIENT, client.toString()))
                .andExpect(status().isNoContent());

        mvc.perform(get("/api/problems").param("bookmarked", "true").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(1))
                .andExpect(jsonPath("$.items[0].slug").value("coin-change"))
                .andExpect(jsonPath("$.items[0].bookmarked").value(true));

        mvc.perform(get("/api/progress").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.bookmarked").value(1));

        mvc.perform(delete("/api/problems/coin-change/bookmark").header(CLIENT, client.toString()))
                .andExpect(status().isNoContent());
        mvc.perform(get("/api/problems").param("bookmarked", "true").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.totalElements").value(0));
    }

    @Test
    void bookmarkingUnknownProblemIs404() throws Exception {
        mvc.perform(put("/api/problems/nope/bookmark").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isNotFound());
    }

    @Test
    void customInputRunsOnceAgainstThatInputAndIsNotPersisted() throws Exception {
        UUID client = UUID.randomUUID();
        mvc.perform(post("/api/problems/two-sum/run")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of(
                                "language", "python",
                                "code", TestExecutorConfig.SOLVE_TWO_SUM,
                                "customInput", "5\n1 2 3 4 5\n9"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("ACCEPTED"))
                .andExpect(jsonPath("$.total").value(1))
                .andExpect(jsonPath("$.cases.length()").value(1))
                // a trailing newline is added to the custom stdin
                .andExpect(jsonPath("$.cases[0].input").value("5\n1 2 3 4 5\n9\n"))
                .andExpect(jsonPath("$.cases[0].actual").value("3 4\n"))
                .andExpect(jsonPath("$.cases[0].expected").value(nullValue()))
                .andExpect(jsonPath("$.submissionId").value(nullValue()));

        mvc.perform(get("/api/problems/two-sum/submissions").header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void customInputReportsRuntimeErrors() throws Exception {
        mvc.perform(post("/api/problems/two-sum/run")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of(
                                "language", "python",
                                "code", TestExecutorConfig.RUNTIME_ERROR,
                                "customInput", "1\n1\n1"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("RUNTIME_ERROR"))
                .andExpect(jsonPath("$.passed").value(0))
                .andExpect(jsonPath("$.message").value("Runtime error on your custom input."))
                .andExpect(jsonPath("$.cases[0].error").value(containsString("IndexError")));
    }

    @Test
    void blankCustomInputFallsBackToSampleCases() throws Exception {
        mvc.perform(post("/api/problems/two-sum/run")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of(
                                "language", "python",
                                "code", TestExecutorConfig.SOLVE_TWO_SUM,
                                "customInput", "   "))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(2));
    }

    @Test
    void acceptanceRateAppearsAfterSubmissions() throws Exception {
        // climbing-stairs is not used by any other test, so it starts without submissions.
        mvc.perform(get("/api/problems/climbing-stairs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.acceptance").value(nullValue()));

        mvc.perform(post("/api/problems/climbing-stairs/submit")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(
                                Map.of("language", "python", "code", TestExecutorConfig.WRONG_ANSWER))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("WRONG_ANSWER"));

        mvc.perform(get("/api/problems/climbing-stairs"))
                .andExpect(jsonPath("$.acceptance").value(0.0));
        mvc.perform(get("/api/problems").param("q", "climbing-stairs"))
                .andExpect(jsonPath("$.items[0].slug").value("climbing-stairs"))
                .andExpect(jsonPath("$.items[0].acceptance").value(0.0));
    }

    @Test
    void validatesRequests() throws Exception {
        UUID client = UUID.randomUUID();
        // missing client id header
        mvc.perform(post("/api/problems/two-sum/run")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"language\":\"python\",\"code\":\"x\"}"))
                .andExpect(status().isBadRequest());
        // blank code
        mvc.perform(judge("run", client, "python", "   ")).andExpect(status().isBadRequest());
        // unsupported language
        mvc.perform(judge("run", client, "brainfuck", "+")).andExpect(status().isBadRequest());
        // malformed client id
        mvc.perform(post("/api/problems/two-sum/run")
                        .header(CLIENT, "not-a-uuid")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"language\":\"python\",\"code\":\"x\"}"))
                .andExpect(status().isBadRequest());
        // unknown problem
        mvc.perform(post("/api/problems/nope/run")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"language\":\"python\",\"code\":\"x\"}"))
                .andExpect(status().isNotFound());
    }
}
