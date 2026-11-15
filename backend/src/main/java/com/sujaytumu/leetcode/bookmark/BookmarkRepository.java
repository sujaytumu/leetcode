package com.sujaytumu.leetcode.bookmark;

import java.util.Set;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface BookmarkRepository extends JpaRepository<Bookmark, Long> {

    boolean existsByClientIdAndProblemId(UUID clientId, Long problemId);

    void deleteByClientIdAndProblemId(UUID clientId, Long problemId);

    long countByClientId(UUID clientId);

    @Query("select b.problemId from Bookmark b where b.clientId = :clientId")
    Set<Long> findProblemIdsByClientId(@Param("clientId") UUID clientId);
}
