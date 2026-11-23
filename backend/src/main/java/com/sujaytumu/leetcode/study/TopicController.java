package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.study.TopicService.TopicView;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/topics")
public class TopicController {

    private final TopicService service;

    public TopicController(TopicService service) {
        this.service = service;
    }

    /** Every topic with its problem count, difficulty split and the caller's solved count; biggest topics first. */
    @GetMapping
    public List<TopicView> topics(@RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.topics(clientId);
    }
}
