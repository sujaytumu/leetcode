package com.sujaytumu.leetcode.discuss;

import java.util.Collection;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface CommentVoteRepository extends JpaRepository<CommentVote, Long> {

    boolean existsByCommentIdAndClientId(Long commentId, UUID clientId);

    @Modifying
    @Query("delete from CommentVote v where v.commentId = :commentId and v.clientId = :clientId")
    void remove(@Param("commentId") Long commentId, @Param("clientId") UUID clientId);

    @Modifying
    @Query("delete from CommentVote v where v.commentId in :commentIds")
    void removeAllFor(@Param("commentIds") Collection<Long> commentIds);

    /** Rows of [commentId, votes]. */
    @Query("select v.commentId, count(v) from CommentVote v where v.commentId in :ids group by v.commentId")
    List<Object[]> countByCommentIds(@Param("ids") Collection<Long> ids);

    @Query("select v.commentId from CommentVote v where v.clientId = :clientId and v.commentId in :ids")
    List<Long> findVotedBy(@Param("clientId") UUID clientId, @Param("ids") Collection<Long> ids);
}
