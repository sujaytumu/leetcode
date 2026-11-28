package com.sujaytumu.leetcode.solutionpost;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoRepository;
import java.time.Duration;
import java.time.Instant;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Community solutions: write, edit, delete (author only), list by votes or newest, and upvote. */
@Service
public class SolutionPostService {

    public static final int MAX_TITLE = 120;
    public static final int MAX_BODY = 20_000;
    public static final int MAX_LANGUAGE = 20;
    public static final int MAX_PER_HOUR = 10;
    private static final int EXCERPT = 160;

    public record Summary(
            Long id, String title, String author, String language, String excerpt, Instant createdAt, int score,
            boolean voted, boolean mine) {}

    /** One of the caller's own posts, with the problem it belongs to (for the profile Solutions tab). */
    public record Mine(
            Long id, String slug, String problemTitle, String title, String language, Instant createdAt, int score) {}

    public record Detail(
            Long id, String slug, String title, String author, String language, String body, Instant createdAt,
            Instant updatedAt, int score, boolean voted, boolean mine) {}

    private final SolutionPostRepository posts;
    private final SolutionPostVoteRepository votes;
    private final ProblemRepository problems;
    private final ProfileInfoRepository profiles;

    public SolutionPostService(
            SolutionPostRepository posts,
            SolutionPostVoteRepository votes,
            ProblemRepository problems,
            ProfileInfoRepository profiles) {
        this.posts = posts;
        this.votes = votes;
        this.problems = problems;
        this.profiles = profiles;
    }

    /** "top" = most upvoted first, anything else = newest first. */
    @Transactional(readOnly = true)
    public List<Summary> list(String slug, UUID clientId, String sort) {
        Long problemId = requireProblemId(slug);
        List<SolutionPost> all = posts.findTop200ByProblemIdOrderByIdDesc(problemId);
        if (all.isEmpty()) {
            return List.of();
        }
        List<Long> ids = all.stream().map(SolutionPost::getId).toList();
        Map<Long, Integer> score = scores(ids);
        Set<Long> mineVoted = clientId == null ? Set.of() : new HashSet<>(votes.findVotedBy(clientId, ids));
        List<Summary> out = new java.util.ArrayList<>();
        for (SolutionPost p : all) {
            out.add(new Summary(
                    p.getId(), p.getTitle(), p.getAuthor(), p.getLanguage(), excerpt(p.getBody()), p.getCreatedAt(),
                    score.getOrDefault(p.getId(), 0), mineVoted.contains(p.getId()),
                    clientId != null && clientId.equals(p.getClientId())));
        }
        if ("top".equalsIgnoreCase(sort)) {
            out.sort(Comparator.comparingInt(Summary::score).reversed().thenComparing(Summary::id, Comparator.reverseOrder()));
        } // already newest first otherwise
        return out;
    }

    /** The caller's own posts, newest first. */
    @Transactional(readOnly = true)
    public List<Mine> mine(UUID clientId) {
        List<SolutionPost> own = posts.findTop100ByClientIdOrderByIdDesc(clientId);
        if (own.isEmpty()) {
            return List.of();
        }
        Map<Long, Integer> score = scores(own.stream().map(SolutionPost::getId).toList());
        List<Mine> out = new java.util.ArrayList<>();
        for (SolutionPost p : own) {
            var problem = problems.findById(p.getProblemId());
            out.add(new Mine(
                    p.getId(), problem.map(pr -> pr.getSlug()).orElse(""), problem.map(pr -> pr.getTitle()).orElse(""),
                    p.getTitle(), p.getLanguage(), p.getCreatedAt(), score.getOrDefault(p.getId(), 0)));
        }
        return out;
    }

    @Transactional(readOnly = true)
    public Detail get(Long id, UUID clientId) {
        SolutionPost p = require(id);
        return detail(p, clientId);
    }

    @Transactional
    public Detail create(String slug, UUID clientId, String rawTitle, String rawBody, String rawLanguage) {
        Long problemId = requireProblemId(slug);
        String title = validTitle(rawTitle);
        String body = validBody(rawBody);
        if (posts.countByClientIdAndCreatedAtAfter(clientId, Instant.now().minus(Duration.ofHours(1))) >= MAX_PER_HOUR) {
            throw new TooManyRequestsException("You are posting too fast. Try again later.");
        }
        SolutionPost saved = posts.save(new SolutionPost(problemId, clientId, authorName(clientId), title, body, language(rawLanguage)));
        return detail(saved, clientId);
    }

    @Transactional
    public Detail update(Long id, UUID clientId, String rawTitle, String rawBody, String rawLanguage) {
        SolutionPost p = requireOwned(id, clientId);
        p.edit(validTitle(rawTitle), validBody(rawBody), language(rawLanguage));
        return detail(posts.save(p), clientId);
    }

    @Transactional
    public void delete(Long id, UUID clientId) {
        SolutionPost p = requireOwned(id, clientId);
        votes.removeAllFor(p.getId());
        posts.delete(p);
    }

    @Transactional
    public void vote(Long id, UUID clientId, boolean on) {
        require(id);
        if (on) {
            if (!votes.existsByPostIdAndClientId(id, clientId)) {
                try {
                    votes.saveAndFlush(new SolutionPostVote(id, clientId));
                } catch (DataIntegrityViolationException raced) {
                    // a concurrent identical vote won; the end state is the same
                }
            }
        } else {
            votes.remove(id, clientId);
        }
    }

    // ---------------------------------------------------------------- helpers

    private Detail detail(SolutionPost p, UUID clientId) {
        int score = scores(List.of(p.getId())).getOrDefault(p.getId(), 0);
        boolean voted = clientId != null && votes.existsByPostIdAndClientId(p.getId(), clientId);
        String slug = problems.findById(p.getProblemId()).map(pr -> pr.getSlug()).orElse("");
        return new Detail(
                p.getId(), slug, p.getTitle(), p.getAuthor(), p.getLanguage(), p.getBody(), p.getCreatedAt(),
                p.getUpdatedAt(), score, voted, clientId != null && clientId.equals(p.getClientId()));
    }

    private Map<Long, Integer> scores(List<Long> ids) {
        Map<Long, Integer> score = new HashMap<>();
        votes.countByPostIds(ids).forEach(r -> score.put(((Number) r[0]).longValue(), ((Number) r[1]).intValue()));
        return score;
    }

    private SolutionPost require(Long id) {
        return posts.findById(id).orElseThrow(() -> new NotFoundException("Solution not found: " + id));
    }

    /** Other people's posts look like they do not exist, so ids cannot be probed. */
    private SolutionPost requireOwned(Long id, UUID clientId) {
        SolutionPost p = require(id);
        if (!p.getClientId().equals(clientId)) {
            throw new NotFoundException("Solution not found: " + id);
        }
        return p;
    }

    private static String validTitle(String raw) {
        String title = raw == null ? "" : raw.strip();
        if (title.isEmpty() || title.length() > MAX_TITLE) {
            throw new IllegalArgumentException("Title must be 1-" + MAX_TITLE + " characters");
        }
        return title;
    }

    private static String validBody(String raw) {
        String body = raw == null ? "" : raw.strip();
        if (body.length() < 10 || body.length() > MAX_BODY) {
            throw new IllegalArgumentException("Solution must be 10-" + MAX_BODY + " characters");
        }
        return body;
    }

    private static String language(String raw) {
        String lang = raw == null ? "" : raw.strip();
        if (lang.isEmpty()) {
            return null;
        }
        return lang.length() > MAX_LANGUAGE ? lang.substring(0, MAX_LANGUAGE) : lang;
    }

    static String excerpt(String body) {
        String flat = body.replaceAll("[\\r\\n]+", " ").replaceAll("[#*`>]+", "").strip();
        return flat.length() <= EXCERPT ? flat : flat.substring(0, EXCERPT) + "…";
    }

    private String authorName(UUID clientId) {
        String name = profiles.findById(clientId)
                .map(p -> !p.getUsername().isBlank() ? p.getUsername() : p.getDisplayName())
                .orElse("");
        if (name == null || name.isBlank()) {
            return "user-" + clientId.toString().substring(0, 4);
        }
        return name.length() > 60 ? name.substring(0, 60) : name;
    }

    private Long requireProblemId(String slug) {
        return problems.findLightBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug)).getId();
    }
}
