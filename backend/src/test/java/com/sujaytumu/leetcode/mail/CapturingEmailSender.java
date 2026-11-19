package com.sujaytumu.leetcode.mail;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/** Records emails instead of sending them. */
public class CapturingEmailSender implements EmailSender {

    public final List<Message> sent = new CopyOnWriteArrayList<>();

    @Override
    public boolean send(Message message) {
        sent.add(message);
        return true;
    }

    public List<Message> to(String email) {
        return sent.stream().filter(m -> m.to().equals(email)).toList();
    }
}
