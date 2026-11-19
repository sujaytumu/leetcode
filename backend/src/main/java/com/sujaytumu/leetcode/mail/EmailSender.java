package com.sujaytumu.leetcode.mail;

public interface EmailSender {

    /** {@code unsubscribeUrl} may be null; when set it is sent as a List-Unsubscribe header. */
    record Message(String to, String subject, String html, String text, String unsubscribeUrl) {}

    /** Sends one email and returns true when it was accepted for delivery. Never throws. */
    boolean send(Message message);
}
