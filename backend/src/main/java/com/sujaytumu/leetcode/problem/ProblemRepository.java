package com.sujaytumu.leetcode.problem;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProblemRepository extends JpaRepository<Problem, Long>, JpaSpecificationExecutor<Problem> {

    // Fetch ONLY testCases. Also fetch-joining the tags collection makes a cartesian product, and because
    // testCases is a List (a Hibernate "bag") every test case would be duplicated once per tag. Tags are
    // loaded lazily (batched) by callers that run inside a transaction.
    @EntityGraph(attributePaths = {"testCases"})
    Optional<Problem> findBySlug(String slug);

    /**
     * Same lookup without the test cases. Use it whenever only the id, slug, title or tags are needed: loading every
     * test case (some are tens of kilobytes) for each request was a large part of the app's lag.
     */
    @Query("select p from Problem p where p.slug = :slug")
    Optional<Problem> findLightBySlug(@Param("slug") String slug);

    /** Just the sample cases of a problem, in order: what the problem page and "Run" need. */
    @Query("select t from TestCase t where t.problem.id = :problemId and t.sample = true")
    List<TestCase> findSamplesUnordered(@Param("problemId") Long problemId);

    default List<TestCase> findSamples(Long problemId) {
        List<TestCase> samples = new ArrayList<>(findSamplesUnordered(problemId));
        samples.sort(Comparator.comparingInt(TestCase::getPosition));
        return samples;
    }

    /** Startup seeding: every problem's slug and study-path position in one query (slug, sortOrder). */
    @Query("select p.slug, p.sortOrder from Problem p")
    List<Object[]> findAllSlugsAndOrders();

    /** Startup seeding: every (slug, tag) pair in one query, instead of loading each problem to read its tags. */
    @Query("select p.slug, t from Problem p join p.tags t")
    List<Object[]> findAllSlugTagPairs();

    @Modifying
    @Query("update Problem p set p.sortOrder = :sortOrder where p.slug = :slug")
    int updateSortOrder(@Param("slug") String slug, @Param("sortOrder") Integer sortOrder);

    @Query("select distinct t from Problem p join p.tags t order by t")
    List<String> findAllTags();

    @Query("select p.difficulty, count(p) from Problem p group by p.difficulty")
    List<Object[]> countByDifficulty();
}
