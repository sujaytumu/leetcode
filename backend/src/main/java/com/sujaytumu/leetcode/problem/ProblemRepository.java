package com.sujaytumu.leetcode.problem;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;

public interface ProblemRepository extends JpaRepository<Problem, Long>, JpaSpecificationExecutor<Problem> {

    @EntityGraph(attributePaths = {"tags", "testCases"})
    Optional<Problem> findBySlug(String slug);

    @Query("select distinct t from Problem p join p.tags t order by t")
    List<String> findAllTags();

    @Query("select p.difficulty, count(p) from Problem p group by p.difficulty")
    List<Object[]> countByDifficulty();
}
