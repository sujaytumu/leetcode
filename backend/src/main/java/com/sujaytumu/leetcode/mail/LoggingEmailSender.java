package com.sujaytumu.leetcode.mail;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Used when no Resend key is configured: nothing leaves the server. */
public class LoggingEmailSender implements EmailSender {

    private static final Logger log = LoggerFactory.getLogger(LoggingEmailSender.class);

    @Override
    public boolean send(Message message) {
        log.info("Email is disabled (set RESEND_API_KEY). Not sending \"{}\".", message.subject());
        return false;
    }
}
