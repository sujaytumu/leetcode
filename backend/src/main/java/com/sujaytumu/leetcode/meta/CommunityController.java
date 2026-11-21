package com.sujaytumu.leetcode.meta;

import com.sujaytumu.leetcode.auth.AccountRepository;
import com.sujaytumu.leetcode.submission.SubmissionRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Public, anonymous totals: how many people use the site. No personal data. */
@RestController
@RequestMapping("/api/community")
public class CommunityController {

    /**
     * @param accounts    registered accounts
     * @param coders      different people (registered or anonymous) who have submitted at least once
     * @param submissions all submissions
     */
    public record Community(long accounts, long coders, long submissions) {}

    private final AccountRepository accounts;
    private final SubmissionRepository submissions;

    public CommunityController(AccountRepository accounts, SubmissionRepository submissions) {
        this.accounts = accounts;
        this.submissions = submissions;
    }

    @GetMapping
    public Community community() {
        return new Community(accounts.count(), submissions.countDistinctClients(), submissions.count());
    }
}
