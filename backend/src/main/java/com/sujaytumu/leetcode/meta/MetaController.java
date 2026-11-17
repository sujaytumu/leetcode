package com.sujaytumu.leetcode.meta;

import com.sujaytumu.leetcode.judge.Language;
import com.sujaytumu.leetcode.problem.Difficulty;
import com.sujaytumu.leetcode.problem.ProblemController;
import com.sujaytumu.leetcode.problem.StatusFilter;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Static vocabulary the UI needs to render filters and the editor: supported languages, difficulty and status
 * options and paging defaults. Derived from the backend enums so the frontend never hardcodes them.
 */
@RestController
@RequestMapping("/api/meta")
public class MetaController {

    public record Option(String key, String label) {}

    public record LanguageOption(String key, String label, String editorMode) {}

    public record Meta(
            List<Option> difficulties,
            List<Option> statuses,
            List<LanguageOption> languages,
            String defaultLanguage,
            int pageSize) {}

    @GetMapping
    public Meta meta() {
        List<LanguageOption> languages = Arrays.stream(Language.values())
                .map(language -> new LanguageOption(language.key(), language.label(), language.editorMode()))
                .toList();
        return new Meta(
                Arrays.stream(Difficulty.values())
                        .map(difficulty -> new Option(difficulty.name(), capitalize(difficulty.name())))
                        .toList(),
                Arrays.stream(StatusFilter.values())
                        .map(status -> new Option(status.name(), capitalize(status.name())))
                        .toList(),
                languages,
                languages.get(0).key(),
                Integer.parseInt(ProblemController.DEFAULT_PAGE_SIZE));
    }

    private static String capitalize(String enumName) {
        return enumName.charAt(0) + enumName.substring(1).toLowerCase(Locale.ROOT);
    }
}
