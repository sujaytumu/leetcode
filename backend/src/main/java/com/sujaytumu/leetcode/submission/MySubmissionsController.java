package com.sujaytumu.leetcode.submission;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.common.PageResponse;
import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** The caller's submissions across every problem, newest first (code is not included; open the problem for that). */
@RestController
@RequestMapping("/api/submissions")
public class MySubmissionsController {

    public record Item(
            Long id,
            String slug,
            String title,
            Verdict verdict,
            Language language,
            int passed,
            int total,
            Integer runtimeMs,
            Integer memoryKb,
            Instant createdAt) {}

    private final SubmissionRepository submissions;
    private final ProblemRepository problems;

    public MySubmissionsController(SubmissionRepository submissions, ProblemRepository problems) {
        this.submissions = submissions;
        this.problems = problems;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public PageResponse<Item> mine(
            @RequestHeader(Headers.CLIENT_ID) UUID clientId,
            @RequestParam(required = false) Verdict verdict,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageRequest paging = PageRequest.of(Math.max(0, page), Math.max(1, Math.min(size, 100)), Sort.by("id").descending());
        Page<Submission> result = verdict == null
                ? submissions.findByClientId(clientId, paging)
                : submissions.findByClientIdAndVerdict(clientId, verdict, paging);
        Set<Long> ids = result.getContent().stream().map(Submission::getProblemId).collect(Collectors.toSet());
        Map<Long, Problem> byId = new HashMap<>();
        problems.findAllById(ids).forEach(p -> byId.put(p.getId(), p));
        return PageResponse.of(result.map(s -> {
            Problem p = byId.get(s.getProblemId());
            return new Item(
                    s.getId(),
                    p == null ? "" : p.getSlug(),
                    p == null ? "(removed problem)" : p.getTitle(),
                    s.getVerdict(),
                    s.getLanguage(),
                    s.getPassedCount(),
                    s.getTotalCount(),
                    s.getRuntimeMs(),
                    s.getMemoryKb(),
                    s.getCreatedAt());
        }));
    }
}
