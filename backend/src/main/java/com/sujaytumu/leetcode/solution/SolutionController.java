package com.sujaytumu.leetcode.solution;

import com.sujaytumu.leetcode.solution.SolutionService.Answer;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class SolutionController {

    private final SolutionService service;

    public SolutionController(SolutionService service) {
        this.service = service;
    }

    /** The reference answer in every language available for the problem; 204 when none has been published yet. */
    @GetMapping("/problems/{slug}/solution")
    public ResponseEntity<Answer> solution(@PathVariable String slug) {
        return service.answer(slug).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.noContent().build());
    }
}
