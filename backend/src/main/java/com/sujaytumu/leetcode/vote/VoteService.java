package com.sujaytumu.leetcode.vote;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.problem.Problem;
import com.sujaytumu.leetcode.problem.ProblemRepository;
import java.util.Optional;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class VoteService {

    public enum VoteType {
        LIKE(1),
        DISLIKE(-1);

        private final int value;

        VoteType(int value) {
            this.value = value;
        }

        int value() {
            return value;
        }

        static VoteType fromValue(int value) {
            return value > 0 ? LIKE : DISLIKE;
        }

        public static VoteType parse(String text) {
            if (text == null) {
                throw new IllegalArgumentException("vote must be LIKE or DISLIKE");
            }
            try {
                return valueOf(text.trim().toUpperCase());
            } catch (IllegalArgumentException ex) {
                throw new IllegalArgumentException("vote must be LIKE or DISLIKE");
            }
        }
    }

    /** {@code myVote} is null when the caller has not voted (or is anonymous). */
    public record VoteSummary(long likes, long dislikes, VoteType myVote) {}

    private final ProblemVoteRepository votes;
    private final ProblemRepository problems;

    public VoteService(ProblemVoteRepository votes, ProblemRepository problems) {
        this.votes = votes;
        this.problems = problems;
    }

    @Transactional(readOnly = true)
    public VoteSummary summary(String slug, UUID clientId) {
        return summarize(requireProblem(slug), clientId);
    }

    /** Sets or switches the caller's vote; voting the same way twice is a no-op. */
    @Transactional
    public VoteSummary vote(String slug, UUID clientId, VoteType type) {
        Problem problem = requireProblem(slug);
        Optional<ProblemVote> existing = votes.findByClientIdAndProblemId(clientId, problem.getId());
        if (existing.isPresent()) {
            existing.get().setScore(type.value());
            votes.saveAndFlush(existing.get());
        } else {
            try {
                votes.saveAndFlush(new ProblemVote(clientId, problem.getId(), type.value()));
            } catch (DataIntegrityViolationException concurrentInsert) {
                ProblemVote winner = votes.findByClientIdAndProblemId(clientId, problem.getId()).orElseThrow();
                winner.setScore(type.value());
                votes.saveAndFlush(winner);
            }
        }
        return summarize(problem, clientId);
    }

    @Transactional
    public VoteSummary clear(String slug, UUID clientId) {
        Problem problem = requireProblem(slug);
        votes.deleteByClientIdAndProblemId(clientId, problem.getId());
        votes.flush();
        return summarize(problem, clientId);
    }

    private VoteSummary summarize(Problem problem, UUID clientId) {
        VoteType mine = clientId == null
                ? null
                : votes.findByClientIdAndProblemId(clientId, problem.getId())
                        .map(vote -> VoteType.fromValue(vote.getScore()))
                        .orElse(null);
        return new VoteSummary(
                votes.countByProblemIdAndScore(problem.getId(), VoteType.LIKE.value()),
                votes.countByProblemIdAndScore(problem.getId(), VoteType.DISLIKE.value()),
                mine);
    }

    private Problem requireProblem(String slug) {
        return problems.findBySlug(slug).orElseThrow(() -> new NotFoundException("Problem not found: " + slug));
    }
}
