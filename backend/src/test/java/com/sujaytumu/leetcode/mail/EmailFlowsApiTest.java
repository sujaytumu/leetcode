package com.sujaytumu.leetcode.mail;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@Import(TestMailConfig.class)
class EmailFlowsApiTest {

    private static final AtomicInteger SEQ = new AtomicInteger();
    private static final Pattern TOKEN = Pattern.compile("token=([A-Za-z0-9_.-]+)");

    @Autowired MockMvc mvc;
    @Autowired CapturingEmailSender mail;
    @Autowired DailyEmailJob job;

    private final ObjectMapper json = new ObjectMapper();

    private static String email() {
        return "mailer" + SEQ.incrementAndGet() + "@example.com";
    }

    private String register(String email, boolean daily) throws Exception {
        return mvc.perform(post("/api/auth/register")
                        .header("X-Client-Id", UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"correct horse\",\"dailyEmail\":" + daily + "}"))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
    }

    private String lastToken(String email, String subjectPart) {
        await().atMost(Duration.ofSeconds(3)).until(() -> mail.to(email).stream().anyMatch(m -> m.subject().contains(subjectPart)));
        var msg = mail.to(email).stream().filter(m -> m.subject().contains(subjectPart)).reduce((a, b) -> b).orElseThrow();
        Matcher m = TOKEN.matcher(msg.text());
        assertTrue(m.find(), "email should contain a token link");
        return m.group(1);
    }

    @Test
    void forgotPasswordEmailsAOneTimeLinkThatSetsANewPasswordAndSignsIn() throws Exception {
        String email = email();
        register(email, false);

        mvc.perform(post("/api/auth/forgot").contentType(MediaType.APPLICATION_JSON).content("{\"email\":\"" + email.toUpperCase() + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ok").value(true));
        String token = lastToken(email, "Reset your");

        mvc.perform(post("/api/auth/reset").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"token\":\"" + token + "\",\"password\":\"brand new pass\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value(email));

        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"brand new pass\"}"))
                .andExpect(status().isOk());
        mvc.perform(post("/api/auth/login").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"correct horse\"}"))
                .andExpect(status().isUnauthorized());

        // The link only works once.
        mvc.perform(post("/api/auth/reset").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"token\":\"" + token + "\",\"password\":\"another pass 1\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void forgotPasswordAnswersTheSameForUnknownEmailsAndSendsNothing() throws Exception {
        String unknown = email();
        mvc.perform(post("/api/auth/forgot").contentType(MediaType.APPLICATION_JSON).content("{\"email\":\"" + unknown + "\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ok").value(true));
        Thread.sleep(300);
        assertTrue(mail.to(unknown).isEmpty());
    }

    @Test
    void resetRejectsGarbageTokensAndWeakPasswords() throws Exception {
        mvc.perform(post("/api/auth/reset").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"token\":\"nope\",\"password\":\"correct horse\"}"))
                .andExpect(status().isBadRequest());

        String email = email();
        register(email, false);
        mvc.perform(post("/api/auth/forgot").contentType(MediaType.APPLICATION_JSON).content("{\"email\":\"" + email + "\"}"));
        String token = lastToken(email, "Reset your");
        mvc.perform(post("/api/auth/reset").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"token\":\"" + token + "\",\"password\":\"short\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void dailyEmailPreferenceCanBeToggledByTheOwner() throws Exception {
        String email = email();
        String session = register(email, false);
        String bearer = "Bearer " + json.readTree(session).get("token").asText();

        mvc.perform(get("/api/auth/email-prefs").header("Authorization", bearer))
                .andExpect(status().isOk()).andExpect(jsonPath("$.dailyEmail").value(false)).andExpect(jsonPath("$.email").value(email));
        mvc.perform(put("/api/auth/email-prefs").header("Authorization", bearer)
                        .contentType(MediaType.APPLICATION_JSON).content("{\"dailyEmail\":true}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.dailyEmail").value(true));
        mvc.perform(get("/api/auth/email-prefs")).andExpect(status().isUnauthorized());
    }

    @Test
    void dailyJobSendsOncePerDayToOptedInAccountsAndUnsubscribeLinkStopsIt() throws Exception {
        String optedIn = email(), optedOut = email();
        register(optedIn, true);
        register(optedOut, false);

        ZonedDateTime evening = ZonedDateTime.now(ZoneId.of("UTC")).withHour(23).withMinute(0);
        job.runOnce(evening);
        assertEquals(1, mail.to(optedIn).size());
        assertTrue(mail.to(optedOut).isEmpty());
        var msg = mail.to(optedIn).get(0);
        assertTrue(msg.subject().startsWith("Daily problem: "));
        assertTrue(msg.text().contains("/problems/"));
        assertTrue(msg.unsubscribeUrl().contains("/unsubscribe?token="));

        job.runOnce(evening); // same day: nothing new for this account
        assertEquals(1, mail.to(optedIn).size());

        // Before the configured hour nothing is sent, even for a new day.
        int before = mail.sent.size();
        job.runOnce(evening.plusDays(1).withHour(0));
        assertEquals(before, mail.sent.size());

        Matcher m = TOKEN.matcher(msg.unsubscribeUrl());
        assertTrue(m.find());
        mvc.perform(post("/api/auth/unsubscribe").contentType(MediaType.APPLICATION_JSON).content("{\"token\":\"" + m.group(1) + "\"}"))
                .andExpect(status().isOk());
        job.runOnce(evening.plusDays(1));
        assertEquals(1, mail.to(optedIn).size());
        assertFalse(mail.to(optedIn).isEmpty());

        mvc.perform(post("/api/auth/unsubscribe").contentType(MediaType.APPLICATION_JSON).content("{\"token\":\"forged.value\"}"))
                .andExpect(status().isBadRequest());
    }
}
