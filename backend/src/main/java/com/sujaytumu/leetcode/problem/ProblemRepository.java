package com.sujaytumu.leetcode.problem;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;

public interface ProblemRepository extends JpaRepository<Problem, Long>, JpaSpecificationExecutor<Problem> {

    // Fetch ONLY testCases. Also fetch-joining the tags collection makes a cartesian product, and because
    // testCases is a List (a Hibernate "bag") every test case would be duplicated once per tag. Tags are
    // loaded lazily (batched) by callers that run inside a transaction.
    @EntityGraph(attributePaths = {"testCases"})
    Optional<Problem> findBySlug(String slug);

    @Query("select distinct t from Problem p join p.tags t order by t")
    List<String> findAllTags();

    @Query("select p.difficulty, count(p) from Problem p group by p.difficulty")
    List<Object[]> countByDifficulty();
}
