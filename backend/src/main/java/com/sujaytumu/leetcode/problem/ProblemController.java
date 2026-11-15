package com.sujaytumu.leetcode.problem;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.common.PageResponse;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemDetail;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class ProblemController {

    private static final int MAX_PAGE_SIZE = 100;

    private final ProblemService service;

    public ProblemController(ProblemService service) {
        this.service = service;
    }

    @GetMapping("/problems")
    public PageResponse<ProblemSummary> list(
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String difficulty,
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "false") boolean bookmarked,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        ProblemQuery query = new ProblemQuery(
                q, Difficulty.parse(difficulty), tag, StatusFilter.parse(status), bookmarked);
        int safePage = Math.max(0, page);
        int safeSize = Math.min(MAX_PAGE_SIZE, Math.max(1, size));
        return service.search(query, clientId, safePage, safeSize);
    }

    @GetMapping("/problems/{slug}")
    public ProblemDetail detail(
            @PathVariable String slug,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.detail(slug, clientId);
    }

    @GetMapping("/tags")
    public List<String> tags() {
        return service.tags();
    }
}
