package com.sujaytumu.leetcode.study;

import com.sujaytumu.leetcode.common.Headers;
import com.sujaytumu.leetcode.study.StudyService.Daily;
import com.sujaytumu.leetcode.study.StudyService.DailyCalendar;
import com.sujaytumu.leetcode.study.StudyService.PlanView;
import com.sujaytumu.leetcode.study.StudyService.Study;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.ZoneOffset;
import java.time.format.DateTimeParseException;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class StudyController {

    private final StudyService service;

    public StudyController(StudyService service) {
        this.service = service;
    }

    /** Hints and approach for a problem; 204 when no write-up exists for it. */
    @GetMapping("/problems/{slug}/study")
    public ResponseEntity<Study> study(@PathVariable String slug) {
        return service.study(slug).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.noContent().build());
    }

    @GetMapping("/plans")
    public List<PlanView> plans(@RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        return service.plans(clientId);
    }

    /** The daily challenge; {@code date} (YYYY-MM-DD) lets the browser ask for its own local day, default is today in UTC. */
    @GetMapping("/daily")
    public ResponseEntity<Daily> daily(
            @RequestParam(required = false) String date,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        LocalDate day;
        if (date == null || date.isBlank()) {
            day = LocalDate.now(ZoneOffset.UTC);
        } else {
            try {
                day = LocalDate.parse(date.trim());
            } catch (DateTimeParseException ex) {
                throw new IllegalArgumentException("date must be in YYYY-MM-DD format");
            }
        }
        return service.daily(clientId, day).map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.noContent().build());
    }

    /** Month view of the daily challenge; {@code month} is YYYY-MM, {@code today} (YYYY-MM-DD) bounds it to the user's own date. */
    @GetMapping("/daily/calendar")
    public DailyCalendar dailyCalendar(
            @RequestParam(required = false) String month,
            @RequestParam(required = false) String today,
            @RequestHeader(value = Headers.CLIENT_ID, required = false) UUID clientId) {
        try {
            LocalDate end = today == null || today.isBlank() ? LocalDate.now(ZoneOffset.UTC) : LocalDate.parse(today.trim());
            YearMonth ym = month == null || month.isBlank() ? YearMonth.from(end) : YearMonth.parse(month.trim());
            return service.calendar(clientId, ym, end);
        } catch (DateTimeParseException ex) {
            throw new IllegalArgumentException("month must be YYYY-MM and today YYYY-MM-DD");
        }
    }
}
