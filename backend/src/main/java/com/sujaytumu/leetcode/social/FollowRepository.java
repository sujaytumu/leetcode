package com.sujaytumu.leetcode.social;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

public interface FollowRepository extends JpaRepository<Follow, Long> {

    boolean existsByFollowerIdAndFolloweeId(UUID followerId, UUID followeeId);

    long countByFolloweeId(UUID followeeId);

    long countByFollowerId(UUID followerId);

    @Transactional
    @Modifying
    @Query("delete from Follow f where f.followerId = :follower and f.followeeId = :followee")
    void remove(@Param("follower") UUID follower, @Param("followee") UUID followee);
}
