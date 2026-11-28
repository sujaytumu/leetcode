package com.sujaytumu.leetcode.discuss;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.common.ApiExceptions.TooManyRequestsException;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import com.sujaytumu.leetcode.profileinfo.ProfileInfo;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoRepository;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
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

@Service
public class DiscussService {

    public static final int MAX_BODY = 2000;
    public static final int MAX_PER_HOUR = 20;

    public record CommentView(
            Long id, Long parentId, String author, String body, Instant createdAt, int score, boolean voted, boolean mine) {}

    /** One of the caller's own comments, with the problem it was posted on (for the profile Discuss tab). */
    public record Mine(Long id, String slug, String problemTitle, String body, Instant createdAt, boolean reply, int score) {}

    private final CommentRepository comments;
    private final CommentVoteRepository votes;
    private final ProblemRepository problems;
    private final ProfileInfoRepository profiles;

    public DiscussService(
            CommentRepository comments,
            CommentVoteRepository votes,
            ProblemRepository problems,
            ProfileInfoRepository profiles) {
        this.comments = comments;
        this.votes = votes;
        this.problems = problems;
        this.profiles = profiles;
    }

    /**
     * Flat list; replies carry {@code parentId} so the client can nest them. Top-level comments come first in the
     * requested order ("top" = most upvoted, anything else = newest) and every reply follows its parent, oldest first.
     */
    @Transactional(readOnly = true)
    public List<CommentView> list(String slug, UUID clientId, String sort) {
        Long problemId = requireProblemId(slug);
        List<Comment> all = comments.findTop500ByProblemIdOrderByIdAsc(problemId);
        if (all.isEmpty()) {
            return List.of();
        }
        List<Long> ids = all.stream().map(Comment::getId).toList();
        Map<Long, Integer> score = new HashMap<>();
        votes.countByCommentIds(ids).forEach(r -> score.put(((Number) r[0]).longValue(), ((Number) r[1]).intValue()));
        Set<Long> mineVoted = clientId == null ? Set.of() : new HashSet<>(votes.findVotedBy(clientId, ids));

        List<CommentView> views = new ArrayList<>();
        for (Comment c : all) {
            views.add(new CommentView(
                    c.getId(), c.getParentId(), c.getAuthor(), c.getBody(), c.getCreatedAt(),
                    score.getOrDefault(c.getId(), 0), mineVoted.contains(c.getId()),
                    clientId != null && clientId.equals(c.getClientId())));
        }

        Comparator<CommentView> order = "top".equalsIgnoreCase(sort)
                ? Comparator.comparingInt(CommentView::score).reversed().thenComparing(CommentView::id, Comparator.reverseOrder())
                : Comparator.comparing(CommentView::id, Comparator.reverseOrder());
        Map<Long, List<CommentView>> replies = new HashMap<>();
        List<CommentView> top = new ArrayList<>();
        for (CommentView v : views) {
            if (v.parentId() == null) {
                top.add(v);
            } else {
                replies.computeIfAbsent(v.parentId(), k -> new ArrayList<>()).add(v);
            }
        }
        top.sort(order);
        List<CommentView> out = new ArrayList<>();
        for (CommentView t : top) {
            out.add(t);
            out.addAll(replies.getOrDefault(t.id(), List.of())); // already oldest first
        }
        return out;
    }

    @Transactional
    public CommentView post(String slug, UUID clientId, String rawBody, Long parentId) {
        Long problemId = requireProblemId(slug);
        String body = rawBody == null ? "" : rawBody.strip();
        if (body.isEmpty() || body.length() > MAX_BODY) {
            throw new IllegalArgumentException("Comment must be 1-" + MAX_BODY + " characters");
        }
        if (parentId != null) {
            Comment parent = comments.findById(parentId)
                    .filter(c -> c.getProblemId().equals(problemId))
                    .orElseThrow(() -> new NotFoundException("Comment not found: " + parentId));
            if (parent.getParentId() != null) {
                throw new IllegalArgumentException("Replies can only be added to top-level comments");
            }
        }
        if (comments.countByClientIdAndCreatedAtAfter(clientId, Instant.now().minus(Duration.ofHours(1))) >= MAX_PER_HOUR) {
            throw new TooManyRequestsException("You are commenting too fast. Try again later.");
        }
        Comment saved = comments.save(new Comment(problemId, clientId, parentId, authorName(clientId), body));
        return new CommentView(saved.getId(), parentId, saved.getAuthor(), saved.getBody(), saved.getCreatedAt(), 0, false, true);
    }

    @Transactional
    public void vote(Long commentId, UUID clientId, boolean on) {
        comments.findById(commentId).orElseThrow(() -> new NotFoundException("Comment not found: " + commentId));
        if (on) {
            if (!votes.existsByCommentIdAndClientId(commentId, clientId)) {
                try {
                    votes.saveAndFlush(new CommentVote(commentId, clientId));
                } catch (DataIntegrityViolationException raced) {
                    // a concurrent identical vote won; the end state is the same
                }
            }
        } else {
            votes.remove(commentId, clientId);
        }
    }

    /** Authors can delete their own comment; deleting a top-level comment removes its replies too. */
    @Transactional
    public void delete(Long commentId, UUID clientId) {
        Comment c = comments.findById(commentId).orElseThrow(() -> new NotFoundException("Comment not found: " + commentId));
        if (!c.getClientId().equals(clientId)) {
            throw new NotFoundException("Comment not found: " + commentId); // do not reveal other people's comments
        }
        List<Comment> doomed = new ArrayList<>(comments.findByParentId(commentId));
        doomed.add(c);
        votes.removeAllFor(doomed.stream().map(Comment::getId).toList());
        comments.deleteAll(doomed);
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

    /** The caller's own comments and replies, newest first. */
    @Transactional(readOnly = true)
    public List<Mine> mine(UUID clientId) {
        List<Comment> own = comments.findTop100ByClientIdOrderByIdDesc(clientId);
        List<Mine> out = new ArrayList<>();
        for (Comment c : own) {
            var problem = problems.findById(c.getProblemId());
            out.add(new Mine(
                    c.getId(), problem.map(pr -> pr.getSlug()).orElse(""), problem.map(pr -> pr.getTitle()).orElse(""),
                    c.getBody(), c.getCreatedAt(), c.getParentId() != null, 0));
        }
        return out;
    }

    private Long requireProblemId(String slug) {
        return problems.findLightBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug)).getId();
    }
}
