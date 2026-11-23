package com.sujaytumu.leetcode.problem;

import jakarta.persistence.criteria.Join;
import jakarta.persistence.criteria.Root;
import jakarta.persistence.criteria.Subquery;
import java.util.Collection;
import java.util.Locale;
import org.springframework.data.jpa.domain.Specification;

/** Composable filters for the problem list. Each returns null (no-op) when its input is empty. */
public final class ProblemSpecifications {

    private ProblemSpecifications() {}

    public static Specification<Problem> titleOrSlugContains(String query) {
        if (query == null || query.isBlank()) {
            return null;
        }
        String pattern = "%" + escapeLike(query.trim().toLowerCase(Locale.ROOT)) + "%";
        return (root, cq, cb) -> cb.or(
                cb.like(cb.lower(root.get("title")), pattern, '\\'),
                cb.like(cb.lower(root.get("slug")), pattern, '\\'));
    }

    public static Specification<Problem> hasDifficulty(Difficulty difficulty) {
        if (difficulty == null) {
            return null;
        }
        return (root, cq, cb) -> cb.equal(root.get("difficulty"), difficulty);
    }

    public static Specification<Problem> hasTag(String tag) {
        if (tag == null || tag.isBlank()) {
            return null;
        }
        String normalized = tag.trim().toLowerCase(Locale.ROOT);
        return (root, cq, cb) -> {
            Subquery<Long> sub = cq.subquery(Long.class);
            Root<Problem> inner = sub.from(Problem.class);
            Join<Problem, String> tags = inner.join("tags");
            sub.select(inner.get("id"))
                    .where(cb.equal(inner.get("id"), root.get("id")), cb.equal(cb.lower(tags), normalized));
            return cb.exists(sub);
        };
    }

    public static Specification<Problem> idIn(Collection<Long> ids) {
        return (root, cq, cb) -> ids.isEmpty() ? cb.disjunction() : root.get("id").in(ids);
    }

    public static Specification<Problem> idNotIn(Collection<Long> ids) {
        if (ids.isEmpty()) {
            return null;
        }
        return (root, cq, cb) -> cb.not(root.get("id").in(ids));
    }

    private static String escapeLike(String value) {
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_");
    }
}
