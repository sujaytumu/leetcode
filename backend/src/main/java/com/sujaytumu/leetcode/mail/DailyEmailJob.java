package com.sujaytumu.leetcode.mail;

import com.sujaytumu.leetcode.auth.Account;
import com.sujaytumu.leetcode.auth.AccountRepository;
import com.sujaytumu.leetcode.auth.TokenService;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.StatusFilter;
import com.sujaytumu.leetcode.study.StudyService;
import java.time.DateTimeException;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * Emails the daily problem to accounts that opted in. It checks every 15 minutes and sends once per day after
 * {@code dailyHour} in the configured zone, so a server that was asleep at 08:00 still catches up when it wakes.
 */
@Component
public class DailyEmailJob {

    private static final Logger log = LoggerFactory.getLogger(DailyEmailJob.class);
    /** Resend allows 2 requests per second. */
    private static final long PAUSE_MILLIS = 600;

    private final AccountRepository accounts;
    private final StudyService study;
    private final EmailSender sender;
    private final TokenService tokens;
    private final MailProperties props;

    public DailyEmailJob(
            AccountRepository accounts, StudyService study, EmailSender sender, TokenService tokens, MailProperties props) {
        this.accounts = accounts;
        this.study = study;
        this.sender = sender;
        this.tokens = tokens;
        this.props = props;
    }

    @Scheduled(fixedDelay = 15 * 60_000L, initialDelay = 60_000L)
    public void tick() {
        if (!props.enabled()) {
            return;
        }
        ZoneId zone;
        try {
            zone = ZoneId.of(props.zone());
        } catch (DateTimeException e) {
            zone = ZoneId.of("UTC");
        }
        try {
            int sent = runOnce(ZonedDateTime.now(zone));
            if (sent > 0) {
                log.info("Sent the daily problem to {} account(s).", sent);
            }
        } catch (RuntimeException e) {
            log.warn("Daily email run failed: {}", e.toString());
        }
    }

    /** Sends to every opted-in account that has not had today's email yet; returns how many were sent. */
    public int runOnce(ZonedDateTime now) {
        if (now.getHour() < props.dailyHour()) {
            return 0;
        }
        LocalDate today = now.toLocalDate();
        int sent = 0;
        for (Account account : accounts.findByDailyEmailTrue()) {
            if (account.getEmail() == null || today.equals(account.getLastDailySent())) {
                continue;
            }
            Optional<StudyService.Daily> daily = study.daily(account.getClientId(), today);
            if (daily.isEmpty()) {
                continue;
            }
            ProblemSummary problem = daily.get().problem();
            if (problem.status() == StatusFilter.SOLVED) {
                accounts.markDailySent(account.getId(), today); // already solved: nothing to remind about
                continue;
            }
            String problemLink = props.baseUrl() + "/problems/" + problem.slug();
            String unsubscribeLink = props.baseUrl() + "/unsubscribe?token=" + tokens.unsubscribeToken(account.getId());
            EmailSender.Message message =
                    EmailTemplates.dailyProblem(account.getEmail(), problem.title(), problem.difficulty(), problemLink, unsubscribeLink);
            if (!sender.send(message)) {
                break; // provider trouble: try again at the next tick instead of hammering it
            }
            accounts.markDailySent(account.getId(), today);
            sent++;
            try {
                Thread.sleep(PAUSE_MILLIS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        return sent;
    }
}
