package com.sujaytumu.leetcode.discuss;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.discuss.DiscussService.CommentView;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DiscussController {

    public record PostRequest(String body, Long parentId) {}

    private final DiscussService service;

    public DiscussController(DiscussService service) {
        this.service = service;
    }

    @GetMapping("/api/problems/{slug}/comments")
    public List<CommentView> list(
            @PathVariable String slug,
            @RequestParam(defaultValue = "top") String sort,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.list(slug, clientId, sort);
    }

    @PostMapping("/api/problems/{slug}/comments")
    @ResponseStatus(HttpStatus.CREATED)
    public CommentView post(
            @PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody PostRequest request) {
        return service.post(slug, clientId, request.body(), request.parentId());
    }

    @PutMapping("/api/comments/{id}/vote")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void vote(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.vote(id, clientId, true);
    }

    @DeleteMapping("/api/comments/{id}/vote")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void unvote(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.vote(id, clientId, false);
    }

    @DeleteMapping("/api/comments/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.delete(id, clientId);
    }
}
