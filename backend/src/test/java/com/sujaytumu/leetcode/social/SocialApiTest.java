package com.sujaytumu.leetcode.social;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.sujaytumu.leetcode.TestExecutorConfig;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
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
class SocialApiTest {

    private static final String CLIENT = "X-Client-Id";
    private static final AtomicInteger SEQ = new AtomicInteger();

    @Autowired
    MockMvc mvc;

    private static String name() {
        return "social" + SEQ.incrementAndGet();
    }

    private void setUsername(String client, String username) throws Exception {
        mvc.perform(put("/api/profile/info").header(CLIENT, client).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"displayName\":\"Pat\",\"username\":\"" + username + "\",\"tags\":[]}"))
                .andExpect(status().isOk());
    }

    @Test
    void usernamesAreUniqueIgnoringCase() throws Exception {
        String a = UUID.randomUUID().toString();
        String name = name();
        setUsername(a, name);
        mvc.perform(put("/api/profile/info").header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"" + name.toUpperCase() + "\",\"tags\":[]}"))
                .andExpect(status().isBadRequest());
        setUsername(a, name); // keeping your own name is fine
    }

    @Test
    void publicProfileFollowAndViews() throws Exception {
        String owner = UUID.randomUUID().toString();
        String fan = UUID.randomUUID().toString();
        String handle = name();
        setUsername(owner, handle);

        // Looking at your own profile does not count as a view and cannot be followed.
        mvc.perform(get("/api/users/" + handle).header(CLIENT, owner))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.you").value(true))
                .andExpect(jsonPath("$.profile.community.views").value(0));
        mvc.perform(put("/api/users/" + handle + "/follow").header(CLIENT, owner)).andExpect(status().isBadRequest());

        // A visitor counts once per day, however often they refresh.
        mvc.perform(get("/api/users/" + handle.toUpperCase()).header(CLIENT, fan))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.info.username").value(handle))
                .andExpect(jsonPath("$.you").value(false))
                .andExpect(jsonPath("$.youFollow").value(false));
        mvc.perform(get("/api/users/" + handle).header(CLIENT, fan))
                .andExpect(jsonPath("$.profile.community.views").value(1));

        mvc.perform(put("/api/users/" + handle + "/follow").header(CLIENT, fan)).andExpect(status().isNoContent());
        mvc.perform(put("/api/users/" + handle + "/follow").header(CLIENT, fan)).andExpect(status().isNoContent()); // idempotent
        mvc.perform(get("/api/users/" + handle).header(CLIENT, fan))
                .andExpect(jsonPath("$.youFollow").value(true))
                .andExpect(jsonPath("$.profile.social.followers").value(1));
        mvc.perform(get("/api/profile").header(CLIENT, fan))
                .andExpect(jsonPath("$.social.following").value(1));

        mvc.perform(delete("/api/users/" + handle + "/follow").header(CLIENT, fan)).andExpect(status().isNoContent());
        mvc.perform(get("/api/users/" + handle).header(CLIENT, fan))
                .andExpect(jsonPath("$.youFollow").value(false))
                .andExpect(jsonPath("$.profile.social.followers").value(0));
    }

    @Test
    void unknownUsernamesAreNotFoundAndAnonymousViewersAreFine() throws Exception {
        mvc.perform(get("/api/users/nobody-" + name())).andExpect(status().isNotFound());
        String owner = UUID.randomUUID().toString();
        String handle = name();
        setUsername(owner, handle);
        mvc.perform(get("/api/users/" + handle)).andExpect(status().isOk());
        mvc.perform(get("/api/users/" + handle + "/rating")).andExpect(status().isOk())
                .andExpect(jsonPath("$.attended").value(0));
        mvc.perform(put("/api/users/" + handle + "/follow")).andExpect(status().isBadRequest()); // header required
    }
}
