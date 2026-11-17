package com.sujaytumu.leetcode.lists;

import java.util.Collection;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProblemListItemRepository extends JpaRepository<ProblemListItem, Long> {

    boolean existsByListIdAndProblemId(Long listId, Long problemId);

    void deleteByListIdAndProblemId(Long listId, Long problemId);

    void deleteByListId(Long listId);

    /** Problem ids in the order they were added. */
    @Query("select i.problemId from ProblemListItem i where i.listId = :listId order by i.id asc")
    List<Long> findProblemIds(@Param("listId") Long listId);

    @Query("select i.listId, count(i) from ProblemListItem i where i.listId in :listIds group by i.listId")
    List<Object[]> countByListIds(@Param("listIds") Collection<Long> listIds);

    @Query("select i.listId from ProblemListItem i where i.problemId = :problemId and i.listId in :listIds")
    List<Long> findListIdsContaining(@Param("problemId") Long problemId, @Param("listIds") Collection<Long> listIds);
}
