package com.sujaytumu.leetcode.lists;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.problem.ProblemService;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ListService {

    public static final int MAX_LISTS = 20;
    public static final int MAX_NAME = 60;

    /** {@code contains} is only meaningful when the caller asked about a specific problem. */
    public record ListSummary(Long id, String name, int count, boolean contains) {}

    public record ListDetail(Long id, String name, List<ProblemSummary> problems) {}

    private final ProblemListRepository lists;
    private final ProblemListItemRepository items;
    private final ProblemRepository problems;
    private final ProblemService problemService;

    public ListService(
            ProblemListRepository lists,
            ProblemListItemRepository items,
            ProblemRepository problems,
            ProblemService problemService) {
        this.lists = lists;
        this.items = items;
        this.problems = problems;
        this.problemService = problemService;
    }

    /** All of the client's lists; with {@code slug}, each says whether it already holds that problem. */
    @Transactional(readOnly = true)
    public List<ListSummary> all(UUID clientId, String slug) {
        List<ProblemList> mine = lists.findByClientIdOrderByIdAsc(clientId);
        if (mine.isEmpty()) {
            return List.of();
        }
        List<Long> ids = mine.stream().map(ProblemList::getId).toList();
        Map<Long, Integer> counts = new HashMap<>();
        items.countByListIds(ids).forEach(r -> counts.put(((Number) r[0]).longValue(), ((Number) r[1]).intValue()));
        Set<Long> containing = new HashSet<>();
        if (slug != null && !slug.isBlank()) {
            problems.findBySlug(slug).ifPresent(p -> containing.addAll(items.findListIdsContaining(p.getId(), ids)));
        }
        return mine.stream()
                .map(l -> new ListSummary(l.getId(), l.getName(), counts.getOrDefault(l.getId(), 0), containing.contains(l.getId())))
                .toList();
    }

    @Transactional
    public ListSummary create(UUID clientId, String rawName) {
        String name = rawName == null ? "" : rawName.trim().replaceAll("\\s+", " ");
        if (name.isEmpty() || name.length() > MAX_NAME) {
            throw new IllegalArgumentException("List name must be 1-" + MAX_NAME + " characters");
        }
        if (lists.countByClientId(clientId) >= MAX_LISTS) {
            throw new IllegalArgumentException("You can have at most " + MAX_LISTS + " lists");
        }
        if (lists.existsByClientIdAndNameIgnoreCase(clientId, name)) {
            throw new IllegalArgumentException("You already have a list called \"" + name + "\"");
        }
        ProblemList saved = lists.save(new ProblemList(clientId, name));
        return new ListSummary(saved.getId(), saved.getName(), 0, false);
    }

    @Transactional
    public void delete(UUID clientId, long listId) {
        ProblemList list = owned(clientId, listId);
        items.deleteByListId(list.getId());
        lists.delete(list);
    }

    @Transactional(readOnly = true)
    public ListDetail detail(UUID clientId, long listId) {
        ProblemList list = owned(clientId, listId);
        return new ListDetail(list.getId(), list.getName(), problemService.summaries(items.findProblemIds(listId), clientId));
    }

    /** Idempotent. */
    @Transactional
    public void add(UUID clientId, long listId, String slug) {
        ProblemList list = owned(clientId, listId);
        Problem problem = problem(slug);
        if (items.existsByListIdAndProblemId(list.getId(), problem.getId())) {
            return;
        }
        try {
            items.saveAndFlush(new ProblemListItem(list.getId(), problem.getId()));
        } catch (DataIntegrityViolationException ignoredConcurrentInsert) {
            // same end state as the request that won the race
        }
    }

    @Transactional
    public void remove(UUID clientId, long listId, String slug) {
        ProblemList list = owned(clientId, listId);
        items.deleteByListIdAndProblemId(list.getId(), problem(slug).getId());
    }

    /** A list that is not the caller's looks exactly like one that does not exist. */
    private ProblemList owned(UUID clientId, long listId) {
        return lists.findById(listId)
                .filter(l -> l.getClientId().equals(clientId))
                .orElseThrow(() -> new NotFoundException("List not found: " + listId));
    }

    private Problem problem(String slug) {
        return problems.findBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }
}
