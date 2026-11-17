package com.sujaytumu.leetcode.vote;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProblemVoteRepository extends JpaRepository<ProblemVote, Long> {

    Optional<ProblemVote> findByClientIdAndProblemId(UUID clientId, Long problemId);

    void deleteByClientIdAndProblemId(UUID clientId, Long problemId);

    long countByProblemIdAndScore(Long problemId, int score);
}
