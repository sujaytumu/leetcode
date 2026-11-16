package com.sujaytumu.leetcode.judge;

import com.sujaytumu.leetcode.config.AppProperties;
import java.net.http.HttpClient;
import java.time.Duration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

@Configuration
public class JudgeConfig {

    @Bean
    public CodeExecutor codeExecutor(AppProperties properties) {
        AppProperties.Judge0 judge0 = properties.judge0();
        if (!judge0.enabled()) {
            return new DisabledCodeExecutor();
        }

        HttpClient httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
        JdkClientHttpRequestFactory factory = new JdkClientHttpRequestFactory(httpClient);
        factory.setReadTimeout(Duration.ofSeconds(judge0.readTimeoutSeconds()));

        RestClient.Builder builder = RestClient.builder().baseUrl(judge0.baseUrl()).requestFactory(factory);
        if (judge0.authToken() != null && !judge0.authToken().isBlank()) {
            builder.defaultHeader("X-Auth-Token", judge0.authToken());
        }
        return new Judge0CodeExecutor(builder.build(), judge0.cpuTimeLimitSeconds());
    }
}
