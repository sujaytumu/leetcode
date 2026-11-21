package com.sujaytumu.leetcode.submission;

import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.springframework.data.domain.Pageable;
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

    /** Rows of [problemId, total submissions, accepted submissions] across all clients. */
    @Query("""
            select s.problemId, count(s), sum(case when s.verdict = :accepted then 1 else 0 end)
            from Submission s
            where s.problemId in :ids
            group by s.problemId
            """)
    List<Object[]> acceptanceStats(@Param("ids") Collection<Long> ids, @Param("accepted") Verdict accepted);

    /** Rows of [id, runtimeMs, memoryKb, clientId] (newest first) of accepted submissions for a problem in one language (all clients). */
    @Query("""
            select s.id, s.runtimeMs, s.memoryKb, s.clientId
            from Submission s
            where s.problemId = :problemId and s.language = :language and s.verdict = :verdict
            order by s.id desc
            """)
    List<Object[]> findMeasurements(
            @Param("problemId") Long problemId,
            @Param("language") com.sujaytumu.leetcode.judge.Language language,
            @Param("verdict") Verdict verdict,
            Pageable pageable);

    /** How many different people (registered or anonymous) have ever submitted something. */
    @Query("select count(distinct s.clientId) from Submission s")
    long countDistinctClients();

    /** Timestamps of every submission by a client since the given instant (for the activity calendar). */
    @Query("select s.createdAt from Submission s where s.clientId = :clientId and s.createdAt >= :since")
    List<Instant> findSubmissionTimesSince(@Param("clientId") UUID clientId, @Param("since") Instant since);

    /** Rows of [createdAt, slug, title, difficulty, language], newest first; page the result to limit it. */
    @Query("""
            select s.createdAt, p.slug, p.title, p.difficulty, s.language
            from Submission s, Problem p
            where p.id = s.problemId and s.clientId = :clientId and s.verdict = :verdict
            order by s.createdAt desc
            """)
    List<Object[]> findRecentWithVerdict(
            @Param("clientId") UUID clientId, @Param("verdict") Verdict verdict, Pageable pageable);

    /** Rows of [language, distinct problems solved in it]. */
    @Query("""
            select s.language, count(distinct s.problemId)
            from Submission s
            where s.clientId = :clientId and s.verdict = :verdict
            group by s.language
            """)
    List<Object[]> countSolvedByLanguage(@Param("clientId") UUID clientId, @Param("verdict") Verdict verdict);

    /** Rows of [clientId, difficulty, distinct problems solved] for every client with an accepted submission. */
    @Query("""
            select s.clientId, p.difficulty, count(distinct s.problemId)
            from Submission s, Problem p
            where p.id = s.problemId and s.verdict = :verdict
            group by s.clientId, p.difficulty
            """)
    List<Object[]> solvedByClientAndDifficulty(@Param("verdict") Verdict verdict);

    /** Every submission to the given problems inside [from, to), oldest first (contest scoring). */
    @Query("""
            select s from Submission s
            where s.problemId in :ids and s.createdAt >= :from and s.createdAt < :to
            order by s.createdAt asc
            """)
    List<Submission> findInWindow(
            @Param("ids") Collection<Long> ids, @Param("from") java.time.Instant from, @Param("to") java.time.Instant to);

    org.springframework.data.domain.Page<Submission> findByClientId(UUID clientId, org.springframework.data.domain.Pageable pageable);

    org.springframework.data.domain.Page<Submission> findByClientIdAndVerdict(
            UUID clientId, Verdict verdict, org.springframework.data.domain.Pageable pageable);
}
