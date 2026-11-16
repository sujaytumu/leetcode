package com.sujaytumu.leetcode.bookmark;

import com.sujaytumu.leetcode.common.Headers;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/problems/{slug}/bookmark")
public class BookmarkController {

    private final BookmarkService service;

    public BookmarkController(BookmarkService service) {
        this.service = service;
    }

    @PutMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void add(@PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.add(slug, clientId);
    }

    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void remove(@PathVariable String slug, @RequestHeader(Headers.CLIENT_ID) UUID clientId) {
        service.remove(slug, clientId);
    }
}
