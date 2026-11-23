package com.sujaytumu.leetcode.workspace;

import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
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
import org.springframework.test.web.servlet.ResultActions;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestExecutorConfig.class)
class WorkspaceApiTest {

    private static final String CLIENT = "X-Client-Id";
    private static final String BASE = "/api/problems/two-sum/workspace";

    @Autowired
    MockMvc mvc;

    @Autowired
    ObjectMapper json;

    private ResultActions putJson(String url, UUID client, Map<String, String> body) throws Exception {
        return mvc.perform(put(url)
                .header(CLIENT, client.toString())
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(body)));
    }

    @Test
    void newClientHasAnEmptyWorkspace() throws Exception {
        mvc.perform(get(BASE).header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.notes.content").value(""))
                .andExpect(jsonPath("$.notes.updatedAt").value(0))
                .andExpect(jsonPath("$.drafts.length()").value(0));
    }

    @Test
    void notesAndDraftsRoundTripAndAreRemovable() throws Exception {
        UUID client = UUID.randomUUID();
        putJson(BASE + "/notes", client, Map.of("content", "use a hash map"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.updatedAt").isNumber())
                .andExpect(jsonPath("$.updatedAt").value(not(0)));
        putJson(BASE + "/drafts/java", client, Map.of("code", "class Solution {}")).andExpect(status().isOk());
        putJson(BASE + "/drafts/python", client, Map.of("code", "pass")).andExpect(status().isOk());
        putJson(BASE + "/drafts/java", client, Map.of("code", "class Solution { int x; }")).andExpect(status().isOk());

        mvc.perform(get(BASE).header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.notes.content").value("use a hash map"))
                .andExpect(jsonPath("$.drafts.length()").value(2))
                .andExpect(jsonPath("$.drafts[0].language").value("java"))
                .andExpect(jsonPath("$.drafts[0].code").value("class Solution { int x; }"))
                .andExpect(jsonPath("$.drafts[1].language").value("python"));

        mvc.perform(delete(BASE + "/drafts/java").header(CLIENT, client.toString())).andExpect(status().isNoContent());
        putJson(BASE + "/notes", client, Map.of("content", "")).andExpect(status().isOk());

        mvc.perform(get(BASE).header(CLIENT, client.toString()))
                .andExpect(jsonPath("$.notes.content").value(""))
                .andExpect(jsonPath("$.drafts.length()").value(1))
                .andExpect(jsonPath("$.drafts[0].language").value("python"));
    }

    @Test
    void workspacesArePrivatePerClient() throws Exception {
        UUID owner = UUID.randomUUID();
        putJson(BASE + "/notes", owner, Map.of("content", "secret")).andExpect(status().isOk());
        mvc.perform(get(BASE).header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(jsonPath("$.notes.content").value(""));
    }

    @Test
    void rejectsBadInput() throws Exception {
        UUID client = UUID.randomUUID();
        putJson(BASE + "/drafts/cobol", client, Map.of("code", "x")).andExpect(status().isBadRequest());
        putJson(BASE + "/notes", client, Map.of("content", "x".repeat(20_001))).andExpect(status().isBadRequest());
        putJson("/api/problems/no-such-problem/workspace/notes", client, Map.of("content", "x"))
                .andExpect(status().isNotFound());
    }
}
