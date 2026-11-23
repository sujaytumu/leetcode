package com.sujaytumu.leetcode.solutionpost;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.solutionpost.SolutionPostService.Detail;
import com.sujaytumu.leetcode.solutionpost.SolutionPostService.Summary;
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
public class SolutionPostController {

    public record PostRequest(String title, String body, String language) {}

    private final SolutionPostService service;

    public SolutionPostController(SolutionPostService service) {
        this.service = service;
    }

    @GetMapping("/api/problems/{slug}/solution-posts")
    public List<Summary> list(
            @PathVariable String slug,
            @RequestParam(defaultValue = "top") String sort,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.list(slug, clientId, sort);
    }

    @PostMapping("/api/problems/{slug}/solution-posts")
    @ResponseStatus(HttpStatus.CREATED)
    public Detail create(
            @PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody PostRequest request) {
        return service.create(slug, clientId, request.title(), request.body(), request.language());
    }

    @GetMapping("/api/me/solution-posts")
    public List<SolutionPostService.Mine> mine(@RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        return service.mine(clientId);
    }

    @GetMapping("/api/solution-posts/{id}")
    public Detail get(
            @PathVariable long id, @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.get(id, clientId);
    }

    @PutMapping("/api/solution-posts/{id}")
    public Detail update(
            @PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody PostRequest request) {
        return service.update(id, clientId, request.title(), request.body(), request.language());
    }

    @DeleteMapping("/api/solution-posts/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.delete(id, clientId);
    }

    @PutMapping("/api/solution-posts/{id}/vote")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void vote(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.vote(id, clientId, true);
    }

    @DeleteMapping("/api/solution-posts/{id}/vote")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void unvote(@PathVariable long id, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.vote(id, clientId, false);
    }
}
