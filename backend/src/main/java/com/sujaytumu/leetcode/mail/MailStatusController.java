package com.sujaytumu.leetcode.mail;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Lets the forgot-password page say so when this server has no email provider, instead of promising a link. */
@RestController
@RequestMapping("/api/auth")
public class MailStatusController {

    public record MailStatus(boolean enabled) {}

    private final MailProperties props;

    public MailStatusController(MailProperties props) {
        this.props = props;
    }

    @GetMapping("/mail-status")
    public MailStatus status() {
        return new MailStatus(props.enabled());
    }
}
