package com.sujaytumu.leetcode.study;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemService;
import com.sujaytumu.leetcode.problem.StatusFilter;
import java.io.IOException;
import java.io.InputStream;
import java.time.LocalDate;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

/**
 * Serves the learning content the UI used to hardcode: per-problem hints and approach write-ups
 * (classpath:seed/study.json), curated study plans (classpath:seed/plans.json) and the daily challenge.
 * Content lives with the backend, so it reaches every deployment regardless of what is already in the database.
 */
@Service
public class StudyService {

    /** Everything fetched in one page when building plans/daily; the catalogue is small. */
    private static final int ALL = 1000;

    public record Study(List<String> hints, String approach, String time, String space) {}

    /** A plan matches a problem that has any of {@code tags} (when given) and the {@code difficulty} (when given). */
    public record PlanDefinition(String id, String title, String blurb, List<String> tags, Difficulty difficulty) {}

    public record PlanView(
            String id, String title, String blurb, int total, int solved, List<ProblemSummary> problems) {}

    public record Daily(String date, ProblemSummary problem) {}

    public record DailyDay(String date, ProblemSummary problem, boolean solved) {}

    /** A month of daily challenges up to {@code today}, each flagged with whether the caller has solved it. */
    public record DailyCalendar(String month, int total, int solved, List<DailyDay> days) {}

    private final ProblemService problems;
    private final Map<String, Study> study;
    private final List<PlanDefinition> plans;

    public StudyService(ObjectMapper objectMapper, ProblemService problems) throws IOException {
        this.problems = problems;
        try (InputStream in = new ClassPathResource("seed/study.json").getInputStream()) {
            this.study = objectMapper.readValue(in, new TypeReference<Map<String, Study>>() {});
        }
        try (InputStream in = new ClassPathResource("seed/plans.json").getInputStream()) {
            this.plans = objectMapper.readValue(in, new TypeReference<List<PlanDefinition>>() {});
        }
    }

    public Optional<Study> study(String slug) {
        return Optional.ofNullable(study.get(slug));
    }

    /** Every non-empty plan with its problems (in study order) and the caller's progress. */
    public List<PlanView> plans(UUID clientId) {
        List<ProblemSummary> all = allProblems(clientId);
        return plans.stream()
                .map(plan -> view(plan, all))
                .filter(view -> view.total() > 0)
                .toList();
    }

    /** Same problem for everyone on a given day. */
    public Optional<Daily> daily(UUID clientId, LocalDate day) {
        List<ProblemSummary> all = allProblems(clientId);
        if (all.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(new Daily(day.toString(), all.get(dailyIndex(all.size(), day))));
    }

    /** Every day of {@code month} up to {@code today}: same pick as {@link #daily}, plus the caller's solved flag. */
    public DailyCalendar calendar(UUID clientId, YearMonth month, LocalDate today) {
        List<ProblemSummary> all = allProblems(clientId);
        List<DailyDay> days = new ArrayList<>();
        if (!all.isEmpty()) {
            for (int day = 1; day <= month.lengthOfMonth(); day++) {
                LocalDate date = month.atDay(day);
                if (date.isAfter(today)) {
                    break;
                }
                ProblemSummary problem = all.get(dailyIndex(all.size(), date));
                days.add(new DailyDay(date.toString(), problem, problem.status() == StatusFilter.SOLVED));
            }
        }
        int solved = (int) days.stream().filter(DailyDay::solved).count();
        return new DailyCalendar(month.toString(), days.size(), solved, days);
    }

    /** 32-bit FNV-1a over "y-m-d", reduced modulo the catalogue size. */
    static int dailyIndex(int count, LocalDate day) {
        String key = day.getYear() + "-" + day.getMonthValue() + "-" + day.getDayOfMonth();
        long hash = 2166136261L;
        for (int i = 0; i < key.length(); i++) {
            hash ^= key.charAt(i);
            hash = (hash * 16777619L) & 0xFFFFFFFFL;
        }
        return (int) (hash % count);
    }

    private List<ProblemSummary> allProblems(UUID clientId) {
        return problems.search(new ProblemQuery(null, null, null, null, false), clientId, 0, ALL).items();
    }

    private static PlanView view(PlanDefinition plan, List<ProblemSummary> all) {
        List<ProblemSummary> items = all.stream()
                .filter(problem -> matches(plan, problem))
                .sorted(Comparator.<ProblemSummary, Difficulty>comparing(ProblemSummary::difficulty)
                        .thenComparingInt(StudyService::numberOf))
                .toList();
        int solved = (int) items.stream().filter(p -> p.status() == StatusFilter.SOLVED).count();
        return new PlanView(plan.id(), plan.title(), plan.blurb(), items.size(), solved, items);
    }

    private static boolean matches(PlanDefinition plan, ProblemSummary problem) {
        boolean hasTags = plan.tags() != null && !plan.tags().isEmpty();
        if (hasTags && problem.tags().stream().noneMatch(plan.tags()::contains)) {
            return false;
        }
        return plan.difficulty() == null || plan.difficulty() == problem.difficulty();
    }

    private static int numberOf(ProblemSummary problem) {
        return problem.number() != null ? problem.number() : Math.toIntExact(problem.id());
    }
}
