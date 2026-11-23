package com.sujaytumu.leetcode.lists;

import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProblemListRepository extends JpaRepository<ProblemList, Long> {

    List<ProblemList> findByClientIdOrderByIdAsc(UUID clientId);

    long countByClientId(UUID clientId);

    boolean existsByClientIdAndNameIgnoreCase(UUID clientId, String name);
}
