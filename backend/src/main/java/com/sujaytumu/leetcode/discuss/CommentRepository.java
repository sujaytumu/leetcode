package com.sujaytumu.leetcode.discuss;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommentRepository extends JpaRepository<Comment, Long> {

    List<Comment> findTop500ByProblemIdOrderByIdAsc(Long problemId);

    List<Comment> findByParentId(Long parentId);

    long countByClientIdAndCreatedAtAfter(UUID clientId, Instant after);
}
