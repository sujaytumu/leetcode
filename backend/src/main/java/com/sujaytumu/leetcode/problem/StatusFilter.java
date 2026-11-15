package com.sujaytumu.leetcode.problem;

/** Per-client progress status used for filtering the problem list. */
public enum StatusFilter {
    TODO,
    ATTEMPTED,
    SOLVED;

    public static StatusFilter parse(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return valueOf(value.trim().toUpperCase());
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Unknown status: " + value);
        }
    }
}
