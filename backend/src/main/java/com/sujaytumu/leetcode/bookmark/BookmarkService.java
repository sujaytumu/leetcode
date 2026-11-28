package com.sujaytumu.leetcode.bookmark;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BookmarkService {

    private final BookmarkRepository bookmarks;
    private final ProblemRepository problems;

    public BookmarkService(BookmarkRepository bookmarks, ProblemRepository problems) {
        this.bookmarks = bookmarks;
        this.problems = problems;
    }

    /** Idempotent: bookmarking twice is a no-op. */
    @Transactional
    public void add(String slug, UUID clientId) {
        Problem problem = requireProblem(slug);
        if (bookmarks.existsByClientIdAndProblemId(clientId, problem.getId())) {
            return;
        }
        try {
            bookmarks.saveAndFlush(new Bookmark(clientId, problem.getId()));
        } catch (DataIntegrityViolationException ignoredConcurrentInsert) {
            // Another request created the same bookmark first; the end state is identical.
        }
    }

    @Transactional
    public void remove(String slug, UUID clientId) {
        Problem problem = requireProblem(slug);
        bookmarks.deleteByClientIdAndProblemId(clientId, problem.getId());
    }

    private Problem requireProblem(String slug) {
        return problems.findLightBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }
}
