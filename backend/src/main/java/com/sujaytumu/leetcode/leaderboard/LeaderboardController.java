package com.sujaytumu.leetcode.leaderboard;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.leaderboard.LeaderboardService.Board;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/leaderboard")
public class LeaderboardController {

    private final LeaderboardService service;

    public LeaderboardController(LeaderboardService service) {
        this.service = service;
    }

    @GetMapping
    public Board board(
            @RequestParam(defaultValue = "50") int limit,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.board(clientId, limit);
    }
}
