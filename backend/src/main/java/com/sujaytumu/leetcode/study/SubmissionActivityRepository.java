package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.Verdict;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.Repository;
import org.springframework.data.repository.query.Param;

/** Read-only submission queries used for recommendations. */
public interface SubmissionActivityRepository extends Repository<Submission, Long> {

    /** Rows of [problemId, most recent submission time] for the given verdict. */
    @Query("""
            select s.problemId, max(s.createdAt)
            from Submission s
            where s.clientId = :clientId and s.verdict = :verdict
            group by s.problemId
            """)
    List<Object[]> lastTimePerProblem(@Param("clientId") UUID clientId, @Param("verdict") Verdict verdict);
}
