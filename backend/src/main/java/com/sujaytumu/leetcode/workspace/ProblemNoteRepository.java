package com.sujaytumu.leetcode.workspace;

import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProblemNoteRepository extends JpaRepository<ProblemNote, Long> {

    Optional<ProblemNote> findByClientIdAndProblemId(UUID clientId, Long problemId);
}
