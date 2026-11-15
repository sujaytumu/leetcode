package com.sujaytumu.leetcode.judge;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.Locale;

/** Supported languages with their Judge0 CE (v1.13) language ids. */
public enum Language {
    JAVA("java", 91),
    PYTHON("python", 100),
    JAVASCRIPT("javascript", 93),
    CPP("cpp", 54);

    private final String key;
    private final int judge0Id;

    Language(String key, int judge0Id) {
        this.key = key;
        this.judge0Id = judge0Id;
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
