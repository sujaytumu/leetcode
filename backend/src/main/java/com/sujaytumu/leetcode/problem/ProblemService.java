package com.sujaytumu.leetcode.problem;

import com.sujaytumu.leetcode.bookmark.BookmarkRepository;
import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.common.PageResponse;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemDetail;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemDtos.SampleCase;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import com.sujaytumu.leetcode.submission.Verdict;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProblemService {

    private final ProblemRepository problems;
    private final SubmissionRepository submissions;
    private final BookmarkRepository bookmarks;

    public ProblemService(
            ProblemRepository problems, SubmissionRepository submissions, BookmarkRepository bookmarks) {
        this.problems = problems;
        this.submissions = submissions;
        this.bookmarks = bookmarks;
    }

    @Transactional(readOnly = true)
    public PageResponse<ProblemSummary> search(ProblemQuery query, UUID clientId, int page, int size) {
        boolean needsIdentity = query.status() != null || query.bookmarkedOnly();
        if (needsIdentity && clientId == null) {
            throw new IllegalArgumentException("status and bookmarked filters require the X-Client-Id header");
        }

        ClientState state = ClientState.load(clientId, submissions, bookmarks);

        Specification<Problem> spec = Specification.where(ProblemSpecifications.titleOrSlugContains(query.text()))
                .and(ProblemSpecifications.hasDifficulty(query.difficulty()))
                .and(ProblemSpecifications.hasTag(query.tag()));

        if (query.bookmarkedOnly()) {
            spec = spec.and(ProblemSpecifications.idIn(state.bookmarked));
        }
        if (query.status() != null) {
            spec = spec.and(statusSpec(query.status(), state));
        }

        Page<Problem> result = problems.findAll(spec, PageRequest.of(page, size, Sort.by("id")));
        return PageResponse.of(result.map(problem -> toSummary(problem, state)));
    }

    @Transactional(readOnly = true)
    public ProblemDetail detail(String slug, UUID clientId) {
        Problem problem = problems.findBySlug(slug)
                .orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
        ClientState state = ClientState.load(clientId, submissions, bookmarks);

        List<SampleCase> samples = problem.getTestCases().stream()
                .filter(TestCase::isSample)
                .map(tc -> new SampleCase(tc.getInput(), tc.getExpectedOutput()))
                .toList();

        return new ProblemDetail(
                problem.getId(),
                problem.getSlug(),
                problem.getTitle(),
                problem.getDifficulty(),
                List.copyOf(problem.getTags()),
                problem.getDescription(),
                problem.getStarterCode(),
                samples,
                state.statusOf(problem.getId()),
                state.bookmarked.contains(problem.getId()));
    }

    @Transactional(readOnly = true)
    public List<String> tags() {
        return problems.findAllTags();
    }

    private Specification<Problem> statusSpec(StatusFilter status, ClientState state) {
        return switch (status) {
            case SOLVED -> ProblemSpecifications.idIn(state.solved);
            case ATTEMPTED -> {
                Set<Long> attemptedOnly = new HashSet<>(state.attempted);
                attemptedOnly.removeAll(state.solved);
                yield ProblemSpecifications.idIn(attemptedOnly);
            }
            case TODO -> ProblemSpecifications.idNotIn(state.attempted);
        };
    }

    private ProblemSummary toSummary(Problem problem, ClientState state) {
        return new ProblemSummary(
                problem.getId(),
                problem.getSlug(),
                problem.getTitle(),
                problem.getDifficulty(),
                List.copyOf(problem.getTags()),
                state.statusOf(problem.getId()),
                state.bookmarked.contains(problem.getId()));
    }

    /** Snapshot of one client's progress; empty for anonymous requests. */
    private record ClientState(Set<Long> attempted, Set<Long> solved, Set<Long> bookmarked) {

        static ClientState load(UUID clientId, SubmissionRepository submissions, BookmarkRepository bookmarks) {
            if (clientId == null) {
                return new ClientState(Set.of(), Set.of(), Set.of());
            }
            return new ClientState(
                    submissions.findAttemptedProblemIds(clientId),
                    submissions.findProblemIdsWithVerdict(clientId, Verdict.ACCEPTED),
                    bookmarks.findProblemIdsByClientId(clientId));
        }

        StatusFilter statusOf(Long problemId) {
            if (solved.contains(problemId)) {
                return StatusFilter.SOLVED;
            }
            return attempted.contains(problemId) ? StatusFilter.ATTEMPTED : StatusFilter.TODO;
        }
    }
}
