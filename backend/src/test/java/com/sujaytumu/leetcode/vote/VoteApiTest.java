package com.sujaytumu.leetcode.vote;

import static org.hamcrest.Matchers.nullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.sujaytumu.leetcode.TestExecutorConfig;
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
class VoteApiTest {

    private static final String CLIENT = "X-Client-Id";
    // a slug no other test votes on, so counts are deterministic within the shared test database
    private static final String SLUG = "valid-anagram";

    @Autowired
    MockMvc mvc;

    private void vote(String client, String vote) throws Exception {
        mvc.perform(put("/api/problems/" + SLUG + "/vote")
                        .header(CLIENT, client)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"vote\":\"" + vote + "\"}"))
                .andExpect(status().isOk());
    }

    @Test
    void likesSwitchesAndClearsVotesPerClient() throws Exception {
        String a = UUID.randomUUID().toString();
        String b = UUID.randomUUID().toString();
        long baseLikes = likes();
        long baseDislikes = dislikes();

        vote(a, "LIKE");
        vote(a, "LIKE"); // repeating is a no-op
        vote(b, "DISLIKE");
        mvc.perform(get("/api/problems/" + SLUG + "/votes").header(CLIENT, a))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.likes").value(baseLikes + 1))
                .andExpect(jsonPath("$.dislikes").value(baseDislikes + 1))
                .andExpect(jsonPath("$.myVote").value("LIKE"));

        vote(a, "DISLIKE"); // switching moves the vote
        mvc.perform(get("/api/problems/" + SLUG + "/votes").header(CLIENT, a))
                .andExpect(jsonPath("$.likes").value(baseLikes))
                .andExpect(jsonPath("$.dislikes").value(baseDislikes + 2))
                .andExpect(jsonPath("$.myVote").value("DISLIKE"));

        mvc.perform(delete("/api/problems/" + SLUG + "/vote").header(CLIENT, a))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.dislikes").value(baseDislikes + 1))
                .andExpect(jsonPath("$.myVote").value(nullValue()));
    }

    @Test
    void anonymousCallersSeeCountsButNoVote() throws Exception {
        mvc.perform(get("/api/problems/" + SLUG + "/votes"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.myVote").value(nullValue()));
    }

    @Test
    void rejectsBadVotesAndUnknownProblems() throws Exception {
        mvc.perform(put("/api/problems/" + SLUG + "/vote")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"vote\":\"MEH\"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(get("/api/problems/no-such-problem/votes")).andExpect(status().isNotFound());
    }

    private long likes() throws Exception {
        return read("$.likes");
    }

    private long dislikes() throws Exception {
        return read("$.dislikes");
    }

    private long read(String path) throws Exception {
        String body = mvc.perform(get("/api/problems/" + SLUG + "/votes")).andReturn().getResponse().getContentAsString();
        return ((Number) com.jayway.jsonpath.JsonPath.read(body, path)).longValue();
    }
}
