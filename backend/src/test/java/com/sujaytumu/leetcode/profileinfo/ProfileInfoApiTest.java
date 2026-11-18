package com.sujaytumu.leetcode.profileinfo;

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
class ProfileInfoApiTest {

    private static final String CLIENT = "X-Client-Id";
    private static final java.util.concurrent.atomic.AtomicInteger SEQ = new java.util.concurrent.atomic.AtomicInteger();

    @Autowired
    MockMvc mvc;

    private static String body(String name, String website, String tagsJson) {
        return "{\"displayName\":\"" + name + "\",\"username\":\"sujay_" + SEQ.incrementAndGet() + "\",\"headline\":\"SDE intern\","
                + "\"company\":\"TripFactory\",\"location\":\"India\",\"school\":\"IIIT Nagpur\","
                + "\"website\":\"" + website + "\",\"github\":\"sujaytumu\",\"linkedin\":\"sujay-babu\","
                + "\"tags\":" + tagsJson + "}";
    }

    @Test
    void newClientHasAnEmptyCard() throws Exception {
        mvc.perform(get("/api/profile/info").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.displayName").value(""))
                .andExpect(jsonPath("$.tags.length()").value(0));
    }

    @Test
    void savesAndReturnsTheCardTrimmedAndDeduplicated() throws Exception {
        String client = UUID.randomUUID().toString();
        mvc.perform(put("/api/profile/info").header(CLIENT, client).contentType(MediaType.APPLICATION_JSON)
                        .content(body("  Sujay  ", "https://example.com", "[\"java\",\" java \",\"dsa\",\"\"]")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.displayName").value("Sujay"))
                .andExpect(jsonPath("$.tags.length()").value(2));
        mvc.perform(get("/api/profile/info").header(CLIENT, client))
                .andExpect(jsonPath("$.company").value("TripFactory"))
                .andExpect(jsonPath("$.tags[0]").value("java"))
                .andExpect(jsonPath("$.tags[1]").value("dsa"));
    }

    @Test
    void cardsAreSeparatePerClient() throws Exception {
        mvc.perform(put("/api/profile/info").header(CLIENT, UUID.randomUUID().toString())
                .contentType(MediaType.APPLICATION_JSON).content(body("Someone", "", "[]")));
        mvc.perform(get("/api/profile/info").header(CLIENT, UUID.randomUUID().toString()))
                .andExpect(jsonPath("$.displayName").value(""));
    }

    @Test
    void rejectsInvalidInput() throws Exception {
        String client = UUID.randomUUID().toString();
        mvc.perform(put("/api/profile/info").header(CLIENT, client).contentType(MediaType.APPLICATION_JSON)
                        .content(body("X", "javascript:alert(1)", "[]")))
                .andExpect(status().isBadRequest());
        mvc.perform(put("/api/profile/info").header(CLIENT, client).contentType(MediaType.APPLICATION_JSON)
                        .content(body("X".repeat(41), "", "[]")))
                .andExpect(status().isBadRequest());
        mvc.perform(put("/api/profile/info").header(CLIENT, client).contentType(MediaType.APPLICATION_JSON)
                        .content(body("X", "", "[\"a\",\"b\",\"c\",\"d\",\"e\",\"f\",\"g\",\"h\",\"i\"]")))
                .andExpect(status().isBadRequest());
    }
}
