package com.sujaytumu.leetcode.social;

import com.sujaytumu.leetcode.common.ApiExceptions.NotFoundException;
import com.sujaytumu.leetcode.leaderboard.LeaderboardService;
import com.sujaytumu.leetcode.leaderboard.LeaderboardService.Entry;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoRepository;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoService;
import com.sujaytumu.leetcode.profileinfo.ProfileInfoService.ProfileInfoView;
import com.sujaytumu.leetcode.progress.ProfileService;
import com.sujaytumu.leetcode.progress.ProfileService.ProfileView;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;

/**
 * Public profiles, addressed by the username a person chose. Setting a username is what makes a profile public.
 * Deliberately not {@code @Transactional}: each repository call commits on its own, so a duplicate visit or follow
 * (which the unique constraints reject) cannot poison a surrounding transaction.
 */
@Service
public class PublicProfileService {

    public record PublicProfile(ProfileInfoView info, ProfileView profile, Integer rank, boolean youFollow, boolean you) {}

    private final ProfileInfoRepository infos;
    private final ProfileInfoService infoService;
    private final ProfileService profiles;
    private final LeaderboardService leaderboard;
    private final FollowRepository follows;
    private final ProfileVisitRepository visits;

    public PublicProfileService(
            ProfileInfoRepository infos,
            ProfileInfoService infoService,
            ProfileService profiles,
            LeaderboardService leaderboard,
            FollowRepository follows,
            ProfileVisitRepository visits) {
        this.infos = infos;
        this.infoService = infoService;
        this.profiles = profiles;
        this.leaderboard = leaderboard;
        this.follows = follows;
        this.visits = visits;
    }

    /** The client id behind a username, or 404. */
    public UUID idOf(String username) {
        return infos.findFirstByUsernameIgnoreCase(username == null ? "" : username.trim())
                .map(info -> info.getClientId())
                .orElseThrow(() -> new NotFoundException("No profile with username " + username));
    }

    public PublicProfile get(String username, UUID viewer, ZoneId zone) {
        UUID id = idOf(username);
        boolean you = id.equals(viewer);
        if (viewer != null && !you) {
            recordVisit(id, viewer);
        }
        ProfileView view = profiles.profile(id, zone); // after the visit, so Views includes this one
        Entry mine = leaderboard.board(id, 1).me();
        boolean youFollow = viewer != null && !you && follows.existsByFollowerIdAndFolloweeId(viewer, id);
        return new PublicProfile(infoService.get(id), view, mine == null ? null : mine.rank(), youFollow, you);
    }

    public void follow(UUID viewer, String username) {
        UUID id = idOf(username);
        if (id.equals(viewer)) {
            throw new IllegalArgumentException("You cannot follow yourself");
        }
        if (!follows.existsByFollowerIdAndFolloweeId(viewer, id)) {
            try {
                follows.save(new Follow(viewer, id));
            } catch (DataIntegrityViolationException raced) {
                // a concurrent identical follow won; the end state is the same
            }
        }
    }

    public void unfollow(UUID viewer, String username) {
        follows.remove(viewer, idOf(username));
    }

    private void recordVisit(UUID profile, UUID viewer) {
        LocalDate today = LocalDate.now(ZoneOffset.UTC);
        if (!visits.existsByProfileIdAndViewerIdAndDay(profile, viewer, today)) {
            try {
                visits.save(new ProfileVisit(profile, viewer, today));
            } catch (DataIntegrityViolationException raced) {
                // already counted today
            }
        }
    }
}
