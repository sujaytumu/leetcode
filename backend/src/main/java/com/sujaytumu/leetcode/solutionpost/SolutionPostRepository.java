package com.sujaytumu.leetcode.solutionpost;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SolutionPostRepository extends JpaRepository<SolutionPost, Long> {

    List<SolutionPost> findTop200ByProblemIdOrderByIdDesc(Long problemId);

    List<SolutionPost> findTop100ByClientIdOrderByIdDesc(UUID clientId);

    long countByClientId(UUID clientId);

    long countByClientIdAndCreatedAtAfter(UUID clientId, Instant since);
}
