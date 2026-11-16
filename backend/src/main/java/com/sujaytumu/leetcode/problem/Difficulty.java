package com.sujaytumu.leetcode.problem;

public enum Difficulty {
    EASY,
    MEDIUM,
    HARD;

    /** Case-insensitive parse; returns null for null/blank input. */
    public static Difficulty parse(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return valueOf(value.trim().toUpperCase());
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Unknown difficulty: " + value);
        }
    }
}
