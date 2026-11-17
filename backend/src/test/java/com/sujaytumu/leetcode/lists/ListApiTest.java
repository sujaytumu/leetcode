package com.sujaytumu.leetcode.lists;

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
class ListApiTest {

    private static final String CLIENT = "X-Client-Id";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private long create(String client, String name) throws Exception {
        String body = mvc.perform(post("/api/lists").header(CLIENT, client)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"" + name + "\"}"))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return json.readTree(body).get("id").asLong();
    }

    @Test
    void buildsAListKeepsInsertionOrderAndReportsMembership() throws Exception {
        String me = UUID.randomUUID().toString();
        long id = create(me, "  Interview   prep ");

        mvc.perform(put("/api/lists/" + id + "/problems/valid-anagram").header(CLIENT, me)).andExpect(status().isNoContent());
        mvc.perform(put("/api/lists/" + id + "/problems/two-sum").header(CLIENT, me)).andExpect(status().isNoContent());
        mvc.perform(put("/api/lists/" + id + "/problems/two-sum").header(CLIENT, me)).andExpect(status().isNoContent()); // idempotent

        mvc.perform(get("/api/lists/" + id).header(CLIENT, me))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Interview prep"))
                .andExpect(jsonPath("$.problems", hasSize(2)))
                .andExpect(jsonPath("$.problems[0].slug").value("valid-anagram"))
                .andExpect(jsonPath("$.problems[1].slug").value("two-sum"));

        mvc.perform(get("/api/lists").param("slug", "two-sum").header(CLIENT, me))
                .andExpect(jsonPath("$[0].count").value(2))
                .andExpect(jsonPath("$[0].contains").value(true));
        mvc.perform(get("/api/lists").param("slug", "coin-change").header(CLIENT, me))
                .andExpect(jsonPath("$[0].contains").value(false));

        mvc.perform(delete("/api/lists/" + id + "/problems/valid-anagram").header(CLIENT, me)).andExpect(status().isNoContent());
        mvc.perform(get("/api/lists/" + id).header(CLIENT, me)).andExpect(jsonPath("$.problems", hasSize(1)));

        mvc.perform(delete("/api/lists/" + id).header(CLIENT, me)).andExpect(status().isNoContent());
        mvc.perform(get("/api/lists/" + id).header(CLIENT, me)).andExpect(status().isNotFound());
    }

    @Test
    void listsArePrivateToTheirOwner() throws Exception {
        String owner = UUID.randomUUID().toString();
        String other = UUID.randomUUID().toString();
        long id = create(owner, "Mine");
        mvc.perform(get("/api/lists/" + id).header(CLIENT, other)).andExpect(status().isNotFound());
        mvc.perform(put("/api/lists/" + id + "/problems/two-sum").header(CLIENT, other)).andExpect(status().isNotFound());
        mvc.perform(delete("/api/lists/" + id).header(CLIENT, other)).andExpect(status().isNotFound());
        mvc.perform(get("/api/lists").header(CLIENT, other)).andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void rejectsBadNamesDuplicatesAndUnknownProblems() throws Exception {
        String me = UUID.randomUUID().toString();
        mvc.perform(post("/api/lists").header(CLIENT, me).contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"   \"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(post("/api/lists").header(CLIENT, me).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"" + "x".repeat(61) + "\"}"))
                .andExpect(status().isBadRequest());
        long id = create(me, "Favourites");
        mvc.perform(post("/api/lists").header(CLIENT, me).contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"favourites\"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(put("/api/lists/" + id + "/problems/not-a-problem").header(CLIENT, me)).andExpect(status().isNotFound());
    }

    @Test
    void capsTheNumberOfListsPerClient() throws Exception {
        String me = UUID.randomUUID().toString();
        for (int i = 0; i < ListService.MAX_LISTS; i++) {
            create(me, "List " + i);
        }
        mvc.perform(post("/api/lists").header(CLIENT, me).contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"One too many\"}"))
                .andExpect(status().isBadRequest());
    }
}
