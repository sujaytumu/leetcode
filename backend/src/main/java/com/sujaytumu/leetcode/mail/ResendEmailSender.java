package com.sujaytumu.leetcode.mail;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Sends through Resend's REST API (https://resend.com/docs/api-reference/emails/send-email). */
public class ResendEmailSender implements EmailSender {

    private static final Logger log = LoggerFactory.getLogger(ResendEmailSender.class);
    private static final URI ENDPOINT = URI.create("https://api.resend.com/emails");

    private final MailProperties props;
    private final ObjectMapper mapper;
    private final HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();

    public ResendEmailSender(MailProperties props, ObjectMapper mapper) {
        this.props = props;
        this.mapper = mapper;
    }

    @Override
    public boolean send(Message m) {
        try {
            Map<String, Object> body = new LinkedHashMap<>();
            body.put("from", props.from());
            body.put("to", List.of(m.to()));
            body.put("subject", m.subject());
            body.put("html", m.html());
            body.put("text", m.text());
            if (m.unsubscribeUrl() != null) {
                body.put("headers", Map.of("List-Unsubscribe", "<" + m.unsubscribeUrl() + ">"));
            }
            HttpRequest request = HttpRequest.newBuilder(ENDPOINT)
                    .timeout(Duration.ofSeconds(15))
                    .header("Authorization", "Bearer " + props.apiKey())
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() / 100 == 2) {
                return true;
            }
            String detail = response.body() == null ? "" : response.body();
            log.warn("Resend rejected an email: HTTP {} {}", response.statusCode(), detail.substring(0, Math.min(200, detail.length())));
            return false;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        } catch (Exception e) {
            log.warn("Could not send an email: {}", e.toString());
            return false;
        }
    }
}
