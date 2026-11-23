package com.sujaytumu.leetcode.lists;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.lists.ListService.ListDetail;
import com.sujaytumu.leetcode.lists.ListService.ListSummary;
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
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/lists")
public class ListController {

    public record CreateRequest(String name) {}

    private final ListService service;

    public ListController(ListService service) {
        this.service = service;
    }

    @GetMapping
    public List<ListSummary> all(
            @RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestParam(required = false) String slug) {
        return service.all(clientId, slug);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ListSummary create(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @RequestBody CreateRequest request) {
        return service.create(clientId, request.name());
    }

    @GetMapping("/{id}")
    public ListDetail detail(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @PathVariable long id) {
        return service.detail(clientId, id);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @PathVariable long id) {
        service.delete(clientId, id);
    }

    @PutMapping("/{id}/problems/{slug}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void add(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @PathVariable long id, @PathVariable String slug) {
        service.add(clientId, id, slug);
    }

    @DeleteMapping("/{id}/problems/{slug}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void remove(@RequestHeader(Headers.CLIENT_ID) UUID clientId, @PathVariable long id, @PathVariable String slug) {
        service.remove(clientId, id, slug);
    }
}
