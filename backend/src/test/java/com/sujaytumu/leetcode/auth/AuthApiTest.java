package com.sujaytumu.leetcode.auth;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
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
class AuthApiTest {

    private static final String CLIENT = "X-Client-Id";
    private static final AtomicInteger SEQ = new AtomicInteger();

    @Autowired
    MockMvc mvc;

    private final ObjectMapper json = new ObjectMapper();

    private static String user() {
        return "tester" + SEQ.incrementAndGet() + "x";
    }

    private static String creds(String username, String password) {
        return "{\"username\":\"" + username + "\",\"password\":\"" + password + "\"}";
    }

    private static String signup(String email, String password) {
        return "{\"email\":\"" + email + "\",\"password\":\"" + password + "\"}";
    }

    private JsonNode register(String username, String password, UUID client) throws Exception {
        String body = mvc.perform(post("/api/auth/register")
                        .header(CLIENT, client.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + username + "@example.com\",\"username\":\"" + username + "\",\"password\":\"" + password + "\"}"))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return json.readTree(body);
    }

    @Test
    void registerKeepsAnonymousProgressAndLoginRestoresItOnAnotherDevice() throws Exception {
        UUID device = UUID.randomUUID();
        mvc.perform(put("/api/problems/two-sum/bookmark").header(CLIENT, device.toString()))
                .andExpect(status().isNoContent());

        String name = user();
        JsonNode session = register(name, "correct horse", device);
        assertTrue(session.get("clientId").asText().equals(device.toString()));

        // A second browser logs in and sees the same data, using only the token.
        String login = mvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(creds(name.toUpperCase(), "correct horse")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.clientId").value(device.toString()))
                .andReturn().getResponse().getContentAsString();
        String token = json.readTree(login).get("token").asText();

        mvc.perform(get("/api/problems").param("bookmarked", "true").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[?(@.slug=='two-sum')]").isNotEmpty());
    }

    @Test
    void anAccountsIdNoLongerWorksWithoutLoggingIn() throws Exception {
        UUID device = UUID.randomUUID();
        register(user(), "correct horse", device);

        mvc.perform(get("/api/progress").header(CLIENT, device.toString())).andExpect(status().isUnauthorized());
        // Anonymous ids are unaffected.
        mvc.perform(get("/api/progress").header(CLIENT, UUID.randomUUID().toString())).andExpect(status().isOk());
    }

    @Test
    void tokenOverridesAForgedClientIdHeader() throws Exception {
        UUID mine = UUID.randomUUID();
        String name = user();
        String token = register(name, "correct horse", mine).get("token").asText();

        UUID victim = UUID.randomUUID();
        mvc.perform(put("/api/problems/two-sum/bookmark")
                        .header("Authorization", "Bearer " + token)
                        .header(CLIENT, victim.toString()))
                .andExpect(status().isNoContent());
        // The bookmark landed on the account, not on the forged id.
        mvc.perform(get("/api/problems").param("bookmarked", "true").header(CLIENT, victim.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items.length()").value(0));
    }

    @Test
    void wrongPasswordAndUnknownUserGetTheSameAnswer() throws Exception {
        String name = user();
        register(name, "correct horse", UUID.randomUUID());
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content(creds(name, "nope nope")))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Wrong email or password."));
        mvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(creds("ghost" + SEQ.incrementAndGet(), "nope nope")))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Wrong email or password."));
    }

    @Test
    void duplicateUsernameAndAlreadyClaimedBrowserAreConflicts() throws Exception {
        String name = user();
        UUID device = UUID.randomUUID();
        register(name, "correct horse", device);

        mvc.perform(post("/api/auth/register")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"other" + SEQ.incrementAndGet() + "@example.com\",\"username\":\"" + name.toUpperCase() + "\",\"password\":\"another pass\"}"))
                .andExpect(status().isConflict());
        mvc.perform(post("/api/auth/register")
                        .header(CLIENT, device.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(signup("again" + SEQ.incrementAndGet() + "@example.com", "another pass")))
                .andExpect(status().isConflict());
    }

    @Test
    void rejectsWeakInput() throws Exception {
        for (String body : new String[] {creds("ab", "correct horse"), creds(user(), "short"), creds("bad name!", "correct horse"),
            signup("not-an-email", "correct horse"), signup(user() + "@example.com", "short")}) {
            mvc.perform(post("/api/auth/register")
                            .header(CLIENT, UUID.randomUUID().toString())
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(body))
                    .andExpect(status().isBadRequest());
        }
    }

    @Test
    void meRequiresAValidTokenAndPasswordChangeRevokesOldTokens() throws Exception {
        String name = user();
        String token = register(name, "correct horse", UUID.randomUUID()).get("token").asText();

        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value(name));
        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + token + "x"))
                .andExpect(status().isUnauthorized());

        mvc.perform(post("/api/auth/password")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"currentPassword\":\"correct horse\",\"newPassword\":\"battery staple\"}"))
                .andExpect(status().isOk());

        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + token)).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON).content(creds(name, "battery staple")))
                .andExpect(status().isOk());
    }

    @Test
    void emailSignUpDerivesAUsernameAndLoginWorksWithEmailInAnyCase() throws Exception {
        String email = "Learner" + SEQ.incrementAndGet() + "@Example.com";
        UUID device = UUID.randomUUID();
        String body = mvc.perform(post("/api/auth/register")
                        .header(CLIENT, device.toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(signup(email, "correct horse")))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value(email.toLowerCase()))
                .andReturn().getResponse().getContentAsString();
        assertTrue(json.readTree(body).get("username").asText().matches("^[a-z0-9_]{3,20}$"));

        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email.toUpperCase() + "\",\"password\":\"correct horse\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.clientId").value(device.toString()));

        // The same email cannot be registered twice, even from another browser.
        mvc.perform(post("/api/auth/register")
                        .header(CLIENT, UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(signup(email, "another pass")))
                .andExpect(status().isConflict());
    }

    @Test
    void logoutEverywhereEndsOtherSessionsButKeepsTheCallerSignedIn() throws Exception {
        String name = user();
        String first = register(name, "correct horse", UUID.randomUUID()).get("token").asText();
        String second = json.readTree(mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content(creds(name, "correct horse")))
                .andExpect(status().isOk()).andReturn().getResponse().getContentAsString()).get("token").asText();

        String fresh = json.readTree(mvc.perform(post("/api/auth/logout-all").header("Authorization", "Bearer " + first))
                        .andExpect(status().isOk()).andReturn().getResponse().getContentAsString()).get("token").asText();

        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + first)).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + second)).andExpect(status().isUnauthorized());
        mvc.perform(get("/api/auth/me").header("Authorization", "Bearer " + fresh)).andExpect(status().isOk());
        mvc.perform(post("/api/auth/logout-all")).andExpect(status().isUnauthorized());
    }
}
