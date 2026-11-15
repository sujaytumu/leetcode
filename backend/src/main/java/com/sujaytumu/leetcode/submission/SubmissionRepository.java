package com.sujaytumu.leetcode.submission;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SubmissionRepository extends JpaRepository<Submission, Long> {

    List<Submission> findTop30ByClientIdAndProblemIdOrderByCreatedAtDesc(UUID clientId, Long problemId);

    @Query("select distinct s.problemId from Submission s where s.clientId = :clientId")
    Set<Long> findAttemptedProblemIds(@Param("clientId") UUID clientId);

    @Query("select distinct s.problemId from Submission s where s.clientId = :clientId and s.verdict = :verdict")
    Set<Long> findProblemIdsWithVerdict(@Param("clientId") UUID clientId, @Param("verdict") Verdict verdict);

    @Query("""
            select p.difficulty, count(distinct s.problemId)
            from Submission s, Problem p
            where p.id = s.problemId and s.clientId = :clientId and s.verdict = :verdict
            group by p.difficulty
            """)
    List<Object[]> countSolvedByDifficulty(@Param("clientId") UUID clientId, @Param("verdict") Verdict verdict);
}
