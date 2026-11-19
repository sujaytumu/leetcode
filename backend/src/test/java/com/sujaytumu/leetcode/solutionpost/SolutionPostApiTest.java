package com.sujaytumu.leetcode.solutionpost;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
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
class SolutionPostApiTest {

    private static final String CLIENT = "X-Client-Id";
    private static final String SLUG = "two-sum";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private long write(String client, String title, String body) throws Exception {
        String res = mvc.perform(post("/api/problems/" + SLUG + "/solution-posts").header(CLIENT, client)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(json.writeValueAsString(Map.of("title", title, "body", body, "language", "C++"))))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return json.readTree(res).get("id").asLong();
    }

    @Test
    void postVoteOrderEditAndDelete() throws Exception {
        String alice = UUID.randomUUID().toString();
        String bob = UUID.randomUUID().toString();
        long first = write(alice, "Hash map, one pass", "Store each value's index and look up the complement.");
        long second = write(bob, "Brute force", "Check every pair; O(n^2) but simple.");

        // Bob and a third client upvote Alice's post.
        mvc.perform(put("/api/solution-posts/" + first + "/vote").header(CLIENT, bob)).andExpect(status().isNoContent());
        mvc.perform(put("/api/solution-posts/" + first + "/vote").header(CLIENT, bob)).andExpect(status().isNoContent()); // idempotent
        mvc.perform(put("/api/solution-posts/" + first + "/vote").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isNoContent());

        // "top" puts the upvoted post first even though it is older.
        mvc.perform(get("/api/problems/" + SLUG + "/solution-posts?sort=top").header(CLIENT, bob))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(first))
                .andExpect(jsonPath("$[0].score").value(2))
                .andExpect(jsonPath("$[0].voted").value(true))
                .andExpect(jsonPath("$[0].mine").value(false))
                .andExpect(jsonPath("$[1].id").value(second));
        mvc.perform(get("/api/problems/" + SLUG + "/solution-posts?sort=new").header(CLIENT, alice))
                .andExpect(jsonPath("$[0].id").value(second));

        // Unvote.
        mvc.perform(delete("/api/solution-posts/" + first + "/vote").header(CLIENT, bob)).andExpect(status().isNoContent());
        mvc.perform(get("/api/solution-posts/" + first).header(CLIENT, bob))
                .andExpect(jsonPath("$.score").value(1))
                .andExpect(jsonPath("$.voted").value(false))
                .andExpect(jsonPath("$.slug").value(SLUG));

        // Only the author can edit or delete; others get a 404 as if it did not exist.
        String edit = json.writeValueAsString(Map.of("title", "Hash map", "body", "Single pass with a dictionary.", "language", "Python"));
        mvc.perform(put("/api/solution-posts/" + first).header(CLIENT, bob).contentType(MediaType.APPLICATION_JSON).content(edit))
                .andExpect(status().isNotFound());
        mvc.perform(put("/api/solution-posts/" + first).header(CLIENT, alice).contentType(MediaType.APPLICATION_JSON).content(edit))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Hash map"))
                .andExpect(jsonPath("$.language").value("Python"));
        mvc.perform(delete("/api/solution-posts/" + first).header(CLIENT, bob)).andExpect(status().isNotFound());
        mvc.perform(delete("/api/solution-posts/" + first).header(CLIENT, alice)).andExpect(status().isNoContent());
        mvc.perform(get("/api/solution-posts/" + first)).andExpect(status().isNotFound());
    }

    @Test
    void rejectsBadInputAndUnknownProblems() throws Exception {
        String c = UUID.randomUUID().toString();
        for (Map<String, String> bad : new Map[] {
                Map.of("title", "", "body", "long enough body here"),
                Map.of("title", "ok", "body", "short"),
                Map.of("title", "x".repeat(121), "body", "long enough body here")}) {
            mvc.perform(post("/api/problems/" + SLUG + "/solution-posts").header(CLIENT, c)
                            .contentType(MediaType.APPLICATION_JSON).content(json.writeValueAsString(bad)))
                    .andExpect(status().isBadRequest());
        }
        mvc.perform(get("/api/problems/no-such-problem/solution-posts")).andExpect(status().isNotFound());
        mvc.perform(get("/api/problems/" + SLUG + "/solution-posts").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk());
    }

    @Test
    void profileCountsSolutionsAndReputation() throws Exception {
        String author = UUID.randomUUID().toString();
        long id = write(author, "Two pointers", "Sort first, then walk two pointers inward.");
        mvc.perform(put("/api/solution-posts/" + id + "/vote").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isNoContent());
        mvc.perform(get("/api/profile").header(CLIENT, author))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.community.solutions").value(1))
                .andExpect(jsonPath("$.community.solutionsLastWeek").value(1))
                .andExpect(jsonPath("$.community.reputation").value(1));
        mvc.perform(get("/api/problems/" + SLUG + "/solution-posts").header(CLIENT, author))
                .andExpect(jsonPath("$", hasSize(org.hamcrest.Matchers.greaterThanOrEqualTo(1))));
    }

    @Test
    void mineListsOnlyMyPostsNewestFirstWithProblemInfo() throws Exception {
        String carol = UUID.randomUUID().toString();
        String dave = UUID.randomUUID().toString();
        long a = write(carol, "Carol first", "Carol's first write-up of the approach.");
        long b = write(carol, "Carol second", "Carol's second write-up of the approach.");
        write(dave, "Dave only", "Dave's own write-up of the approach.");

        mvc.perform(get("/api/me/solution-posts").header(CLIENT, carol))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].id").value(b))
                .andExpect(jsonPath("$[1].id").value(a))
                .andExpect(jsonPath("$[0].slug").value(SLUG))
                .andExpect(jsonPath("$[0].problemTitle").isNotEmpty());

        mvc.perform(get("/api/me/solution-posts").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }
}
