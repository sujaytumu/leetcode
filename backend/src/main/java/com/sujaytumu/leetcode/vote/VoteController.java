package com.sujaytumu.leetcode.vote;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.vote.VoteService.VoteSummary;
import com.sujaytumu.leetcode.vote.VoteService.VoteType;
import java.util.UUID;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/problems/{slug}")
public class VoteController {

    public record VoteRequest(String vote) {}

    private final VoteService service;

    public VoteController(VoteService service) {
        this.service = service;
    }

    @GetMapping("/votes")
    public VoteSummary votes(
            @PathVariable String slug, @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.summary(slug, clientId);
    }

    @PutMapping("/vote")
    public VoteSummary vote(
            @PathVariable String slug,
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @RequestBody VoteRequest request) {
        return service.vote(slug, clientId, VoteType.parse(request.vote()));
    }

    @DeleteMapping("/vote")
    public VoteSummary clear(@PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.clear(slug, clientId);
    }
}
