package com.sujaytumu.leetcode.export;

import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemQuery;
import com.sujaytumu.leetcode.problem.ProblemDtos.ProblemSummary;
import com.sujaytumu.leetcode.problem.ProblemService;
import com.sujaytumu.leetcode.submission.Submission;
import com.sujaytumu.leetcode.submission.Verdict;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Builds a zip of a client's accepted solutions, one folder per problem (latest accepted solution per language)
 * plus README indexes, so it can be dropped straight into a GitHub repository.
 */
@Service
public class ExportService {

    private static final int ALL = 1000;

    private final ProblemService problems;
    private final ExportRepository submissions;

    public ExportService(ProblemService problems, ExportRepository submissions) {
        this.problems = problems;
        this.submissions = submissions;
    }

    @Transactional(readOnly = true)
    public byte[] solutionsZip(UUID clientId) throws IOException {
        Map<Long, ProblemSummary> byId = new LinkedHashMap<>();
        for (ProblemSummary summary : problems.search(new ProblemQuery(null, null, null, null, false), clientId, 0, ALL).items()) {
            byId.put(summary.id(), summary);
        }

        // newest first, so the first one seen per problem+language is the latest accepted solution
        Map<String, Submission> latest = new LinkedHashMap<>();
        for (Submission submission : submissions.acceptedNewestFirst(clientId, Verdict.ACCEPTED)) {
            latest.putIfAbsent(submission.getProblemId() + ":" + submission.getLanguage().key(), submission);
        }
        Map<Integer, List<Submission>> byNumber = new TreeMap<>();
        Map<Integer, ProblemSummary> summaryByNumber = new TreeMap<>();
        for (Submission submission : latest.values()) {
            ProblemSummary summary = byId.get(submission.getProblemId());
            if (summary == null) {
                continue;
            }
            int number = numberOf(summary);
            byNumber.computeIfAbsent(number, key -> new ArrayList<>()).add(submission);
            summaryByNumber.put(number, summary);
        }

        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (ZipOutputStream zip = new ZipOutputStream(bytes, StandardCharsets.UTF_8)) {
            StringBuilder index = new StringBuilder("# My LeetCode solutions\n\n");
            if (byNumber.isEmpty()) {
                index.append("No accepted solutions yet.\n");
            } else {
                index.append("| # | Problem | Difficulty | Topics | Languages | Last solved |\n|---|---|---|---|---|---|\n");
            }
            for (Map.Entry<Integer, List<Submission>> entry : byNumber.entrySet()) {
                ProblemSummary summary = summaryByNumber.get(entry.getKey());
                List<Submission> solutions = entry.getValue();
                solutions.sort(Comparator.comparing((Submission s) -> s.getLanguage().key()));
                String folder = String.format("%04d-%s", entry.getKey(), summary.slug());

                StringBuilder readme = new StringBuilder("# " + entry.getKey() + ". " + summary.title() + "\n\n");
                readme.append("- Difficulty: ").append(capitalize(summary.difficulty().name())).append('\n');
                readme.append("- Topics: ").append(String.join(", ", summary.tags())).append("\n\n## Solutions\n\n");
                List<String> languages = new ArrayList<>();
                String lastSolved = "";
                for (Submission solution : solutions) {
                    Language language = solution.getLanguage();
                    String file = "solution." + extension(language);
                    String day = solution.getCreatedAt().toString().substring(0, 10);
                    add(zip, folder + "/" + file, solution.getCode());
                    readme.append("- [").append(file).append("](").append(file).append(") (").append(language.label())
                            .append(", solved ").append(day).append(")\n");
                    languages.add(language.label());
                    if (day.compareTo(lastSolved) > 0) {
                        lastSolved = day;
                    }
                }
                add(zip, folder + "/README.md", readme.toString());
                index.append("| ").append(entry.getKey()).append(" | [").append(summary.title()).append("](")
                        .append(folder).append("/) | ").append(capitalize(summary.difficulty().name())).append(" | ")
                        .append(String.join(", ", summary.tags())).append(" | ").append(String.join(", ", languages))
                        .append(" | ").append(lastSolved).append(" |\n");
            }
            add(zip, "README.md", index.toString());
        }
        return bytes.toByteArray();
    }

    private static void add(ZipOutputStream zip, String name, String content) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(content.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    static String extension(Language language) {
        return switch (language) {
            case JAVA -> "java";
            case PYTHON -> "py";
            case JAVASCRIPT -> "js";
            case CPP -> "cpp";
        };
    }

    private static int numberOf(ProblemSummary summary) {
        return summary.number() != null ? summary.number() : Math.toIntExact(summary.id());
    }

    private static String capitalize(String enumName) {
        return enumName.charAt(0) + enumName.substring(1).toLowerCase();
    }
}
