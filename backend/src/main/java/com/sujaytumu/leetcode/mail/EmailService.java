package com.sujaytumu.leetcode.mail;

import jakarta.annotation.PreDestroy;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.springframework.stereotype.Service;

/** Sends in the background so a request never waits on (or reveals timing of) the mail provider. */
@Service
public class EmailService {

    private final EmailSender sender;
    private final ExecutorService pool = Executors.newFixedThreadPool(2, r -> {
        Thread t = new Thread(r, "mail-sender");
        t.setDaemon(true);
        return t;
    });

    public EmailService(EmailSender sender) {
        this.sender = sender;
    }

    public void sendAsync(EmailSender.Message message) {
        pool.execute(() -> sender.send(message));
    }

    @PreDestroy
    void shutdown() {
        pool.shutdown();
    }
}
