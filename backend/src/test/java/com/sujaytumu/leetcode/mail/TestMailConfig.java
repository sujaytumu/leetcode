package com.sujaytumu.leetcode.mail;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;

@TestConfiguration
public class TestMailConfig {

    @Bean
    @Primary
    public CapturingEmailSender capturingEmailSender() {
        return new CapturingEmailSender();
    }
}
