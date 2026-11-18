package com.sujaytumu.leetcode.solutionpost;

import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SolutionPostVoteRepository extends JpaRepository<SolutionPostVote, Long> {

    boolean existsByPostIdAndClientId(Long postId, UUID clientId);

    @Modifying
    @Query("delete from SolutionPostVote v where v.postId = :postId and v.clientId = :clientId")
    void remove(@Param("postId") Long postId, @Param("clientId") UUID clientId);

    @Modifying
    @Query("delete from SolutionPostVote v where v.postId = :postId")
    void removeAllFor(@Param("postId") Long postId);

    /** Rows of [postId, votes]. */
    @Query("select v.postId, count(v) from SolutionPostVote v where v.postId in :ids group by v.postId")
    List<Object[]> countByPostIds(@Param("ids") Collection<Long> ids);

    @Query("select v.postId from SolutionPostVote v where v.clientId = :clientId and v.postId in :ids")
    List<Long> findVotedBy(@Param("clientId") UUID clientId, @Param("ids") Collection<Long> ids);

    /** Upvotes received on all solutions written by this client. */
    @Query("select count(v) from SolutionPostVote v where v.postId in (select p.id from SolutionPost p where p.clientId = :clientId)")
    long countReceived(@Param("clientId") UUID clientId);

    @Query("select count(v) from SolutionPostVote v where v.createdAt > :since"
            + " and v.postId in (select p.id from SolutionPost p where p.clientId = :clientId)")
    long countReceivedSince(@Param("clientId") UUID clientId, @Param("since") Instant since);
}
