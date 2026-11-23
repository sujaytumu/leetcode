package com.sujaytumu.leetcode.judge;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.Locale;

/** Supported languages with their Judge0 CE (v1.13) language ids. */
public enum Language {
    JAVA("java", 91, "Java", "java"),
    PYTHON("python", 100, "Python", "python"),
    JAVASCRIPT("javascript", 93, "JavaScript", "javascript"),
    CPP("cpp", 54, "C++", "cpp");

    private final String key;
    private final int judge0Id;
    private final String label;
    private final String editorMode;

    Language(String key, int judge0Id, String label, String editorMode) {
        this.key = key;
        this.judge0Id = judge0Id;
        this.label = label;
        this.editorMode = editorMode;
    }

    /** Human-friendly name shown in the language picker. */
    public String label() {
        return label;
    }

    /** Syntax-highlighting mode id understood by the Monaco editor. */
    public String editorMode() {
        return editorMode;
    }

    @JsonValue
    public String key() {
        return key;
    }

    public int judge0Id() {
        return judge0Id;
    }

    @JsonCreator
    public static Language fromKey(String value) {
        if (value != null) {
            String normalized = value.trim().toLowerCase(Locale.ROOT);
            for (Language language : values()) {
                if (language.key.equals(normalized)) {
                    return language;
                }
            }
        }
        throw new IllegalArgumentException("Unsupported language: " + value);
    }
}
