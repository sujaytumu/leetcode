package com.sujaytumu.leetcode.workspace;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CodeDraftRepository extends JpaRepository<CodeDraft, Long> {

    List<CodeDraft> findByClientIdAndProblemId(UUID clientId, Long problemId);

    Optional<CodeDraft> findByClientIdAndProblemIdAndLanguage(UUID clientId, Long problemId, String language);
}
