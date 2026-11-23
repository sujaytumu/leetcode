package com.sujaytumu.leetcode.discuss;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
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
class DiscussApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private long addComment(String slug, String client, String body, Long parent) throws Exception {
        String payload = json.writeValueAsString(java.util.Map.of("body", body, "parentId", parent == null ? "" : parent))
                .replace("\"parentId\":\"\"", "\"parentId\":null");
        String res = mvc.perform(post("/api/problems/" + slug + "/comments").header(CLIENT, client)
                        .contentType(MediaType.APPLICATION_JSON).content(payload))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return json.readTree(res).get("id").asLong();
    }

    @Test
    void commentsRepliesVotesAndOrdering() throws Exception {
        String slug = "valid-parentheses";
        String alice = UUID.randomUUID().toString();
        String bob = UUID.randomUUID().toString();

        long first = addComment(slug, alice, "Use a stack.", null);
        long second = addComment(slug, bob, "A counter is enough for one bracket type.", null);
        long reply = addComment(slug, bob, "Agreed, stack it is.", first);

        mvc.perform(put("/api/comments/" + second + "/vote").header(CLIENT, alice)).andExpect(status().isNoContent());
        mvc.perform(put("/api/comments/" + second + "/vote").header(CLIENT, alice)).andExpect(status().isNoContent()); // idempotent

        // top: most upvoted first; the reply follows its parent
        mvc.perform(get("/api/problems/" + slug + "/comments?sort=top").header(CLIENT, alice))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[0].id").value(second))
                .andExpect(jsonPath("$[0].score").value(1))
                .andExpect(jsonPath("$[0].voted").value(true))
                .andExpect(jsonPath("$[1].id").value(first))
                .andExpect(jsonPath("$[1].mine").value(true))
                .andExpect(jsonPath("$[2].id").value(reply))
                .andExpect(jsonPath("$[2].parentId").value(first))
                .andExpect(jsonPath("$[2].mine").value(false));

        // newest first
        mvc.perform(get("/api/problems/" + slug + "/comments?sort=new"))
                .andExpect(jsonPath("$[0].id").value(second))
                .andExpect(jsonPath("$[0].voted").value(false));

        mvc.perform(delete("/api/comments/" + second + "/vote").header(CLIENT, alice)).andExpect(status().isNoContent());
        mvc.perform(get("/api/problems/" + slug + "/comments?sort=top").header(CLIENT, alice))
                .andExpect(jsonPath("$[0].score").value(0));
    }

    @Test
    void validatesInputAndProtectsOthersComments() throws Exception {
        String slug = "two-sum";
        String alice = UUID.randomUUID().toString();
        String bob = UUID.randomUUID().toString();
        long mine = addComment(slug, alice, "Hash map, O(n).", null);
        long theirReply = addComment(slug, bob, "Nice.", mine);

        mvc.perform(post("/api/problems/" + slug + "/comments").header(CLIENT, alice)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"body\":\"   \"}"))
                .andExpect(status().isBadRequest());
        // replies to replies are rejected
        mvc.perform(post("/api/problems/" + slug + "/comments").header(CLIENT, alice)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"body\":\"x\",\"parentId\":" + theirReply + "}"))
                .andExpect(status().isBadRequest());
        mvc.perform(post("/api/problems/no-such-problem/comments").header(CLIENT, alice)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"body\":\"x\"}"))
                .andExpect(status().isNotFound());

        // another client cannot delete it
        mvc.perform(delete("/api/comments/" + mine).header(CLIENT, bob)).andExpect(status().isNotFound());
        // the author can, and the replies go with it
        mvc.perform(delete("/api/comments/" + mine).header(CLIENT, alice)).andExpect(status().isNoContent());
        mvc.perform(get("/api/problems/" + slug + "/comments")).andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void mineListsOnlyMyCommentsNewestFirstWithProblemInfo() throws Exception {
        String me = UUID.randomUUID().toString();
        String other = UUID.randomUUID().toString();
        long first = addComment("climbing-stairs", me, "Hash map in one pass.", null);
        addComment("climbing-stairs", other, "Not mine.", null);
        addComment("palindrome-number", me, "Stack works.", null);
        addComment("climbing-stairs", me, "Reply to myself.", first);

        mvc.perform(get("/api/me/comments").header(CLIENT, me))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[0].body").value("Reply to myself."))
                .andExpect(jsonPath("$[0].reply").value(true))
                .andExpect(jsonPath("$[1].slug").value("palindrome-number"))
                .andExpect(jsonPath("$[2].problemTitle").value("Climbing Stairs"));

        mvc.perform(get("/api/me/comments").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk()).andExpect(jsonPath("$", hasSize(0)));
    }
}
