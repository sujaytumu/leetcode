package com.sujaytumu.leetcode.export;

import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.Verdict;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.Repository;
import org.springframework.data.repository.query.Param;

/** Read-only query used to export a client's solutions. */
public interface ExportRepository extends Repository<Submission, Long> {

    @Query("select s from Submission s where s.clientId = :clientId and s.verdict = :verdict order by s.createdAt desc")
    List<Submission> acceptedNewestFirst(@Param("clientId") UUID clientId, @Param("verdict") Verdict verdict);
}
