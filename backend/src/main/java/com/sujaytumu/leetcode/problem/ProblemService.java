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
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
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
        return search(query, clientId, page, size, "number", true);
    }

    /**
     * @param sort one of number (study-path order, the default), title, difficulty, acceptance; unknown values mean number
     */
    @Transactional(readOnly = true)
    public PageResponse<ProblemSummary> search(
            ProblemQuery query, UUID clientId, int page, int size, String sort, boolean ascending) {
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

        String key = sort == null ? "number" : sort.toLowerCase(java.util.Locale.ROOT);
        if (key.equals("difficulty") || key.equals("acceptance")) {
            return searchSortedInMemory(spec, state, page, size, key, ascending);
        }
        Sort order = key.equals("title")
                ? Sort.by(ascending ? Sort.Direction.ASC : Sort.Direction.DESC, "title")
                : Sort.by(ascending ? Sort.Direction.ASC : Sort.Direction.DESC, "sortOrder", "id");
        Page<Problem> result = problems.findAll(spec, PageRequest.of(page, size, order));
        Map<Long, Double> acceptance = acceptanceByProblem(result.getContent().stream().map(Problem::getId).toList());
        return PageResponse.of(result.map(problem -> toSummary(problem, state, acceptance.get(problem.getId()))));
    }

    /**
     * Difficulty (an enum stored as text) and acceptance (computed from submissions) cannot be ordered by the
     * database cheaply; the catalogue is small, so sort the filtered set here and slice the page.
     */
    private PageResponse<ProblemSummary> searchSortedInMemory(
            Specification<Problem> spec, ClientState state, int page, int size, String key, boolean ascending) {
        List<Problem> all = problems.findAll(spec, Sort.by("sortOrder", "id"));
        Map<Long, Double> acceptance = acceptanceByProblem(all.stream().map(Problem::getId).toList());
        Comparator<Problem> cmp;
        if (key.equals("difficulty")) {
            Comparator<Problem> byDifficulty = Comparator.comparingInt(p -> p.getDifficulty().ordinal());
            cmp = ascending ? byDifficulty : byDifficulty.reversed();
        } else {
            // Problems nobody has submitted yet have no acceptance rate and always sort last.
            Comparator<Problem> byRate = Comparator.comparingDouble(p -> acceptance.get(p.getId()));
            Comparator<Problem> known = ascending ? byRate : byRate.reversed();
            cmp = (a, b) -> {
                boolean ha = acceptance.containsKey(a.getId());
                boolean hb = acceptance.containsKey(b.getId());
                if (ha != hb) {
                    return ha ? -1 : 1;
                }
                return ha ? known.compare(a, b) : 0;
            };
        }
        List<Problem> sorted = new ArrayList<>(all);
        sorted.sort(cmp); // stable: ties keep study-path order
        int from = (int) Math.min((long) page * size, sorted.size());
        int to = Math.min(sorted.size(), from + size);
        Page<Problem> slice = new org.springframework.data.domain.PageImpl<>(
                sorted.subList(from, to), PageRequest.of(page, size), sorted.size());
        return PageResponse.of(slice.map(problem -> toSummary(problem, state, acceptance.get(problem.getId()))));
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
                state.bookmarked.contains(problem.getId()),
                acceptanceByProblem(List.of(problem.getId())).get(problem.getId()),
                numberOf(problem));
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

    /** Accepted / total submissions as a percentage (one decimal). Problems nobody has submitted are absent. */
    private Map<Long, Double> acceptanceByProblem(Collection<Long> ids) {
        if (ids.isEmpty()) {
            return Map.of();
        }
        Map<Long, Double> result = new HashMap<>();
        for (Object[] row : submissions.acceptanceStats(ids, Verdict.ACCEPTED)) {
            long total = ((Number) row[1]).longValue();
            long accepted = ((Number) row[2]).longValue();
            if (total > 0) {
                result.put(((Number) row[0]).longValue(), Math.round(accepted * 1000.0 / total) / 10.0);
            }
        }
        return result;
    }

    /** Summaries for the given problem ids in that order (unknown ids are skipped), with the caller's progress. */
    @Transactional(readOnly = true)
    public List<ProblemSummary> summaries(List<Long> ids, UUID clientId) {
        if (ids.isEmpty()) {
            return List.of();
        }
        ClientState state = ClientState.load(clientId, submissions, bookmarks);
        Map<Long, Double> acceptance = acceptanceByProblem(ids);
        Map<Long, Problem> byId = new HashMap<>();
        problems.findAllById(ids).forEach(p -> byId.put(p.getId(), p));
        return ids.stream()
                .map(byId::get)
                .filter(java.util.Objects::nonNull)
                .map(p -> toSummary(p, state, acceptance.get(p.getId())))
                .toList();
    }

    private static Integer numberOf(Problem problem) {
        return problem.getSortOrder() != null ? problem.getSortOrder() : Math.toIntExact(problem.getId());
    }

    private ProblemSummary toSummary(Problem problem, ClientState state, Double acceptance) {
        return new ProblemSummary(
                problem.getId(),
                problem.getSlug(),
                problem.getTitle(),
                problem.getDifficulty(),
                List.copyOf(problem.getTags()),
                state.statusOf(problem.getId()),
                state.bookmarked.contains(problem.getId()),
                acceptance,
                numberOf(problem));
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
