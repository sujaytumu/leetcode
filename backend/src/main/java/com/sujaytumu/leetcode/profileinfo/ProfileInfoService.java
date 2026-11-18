package com.sujaytumu.leetcode.profileinfo;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.UUID;
import java.util.regex.Pattern;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProfileInfoService {

    /** Same shape for reading and writing; every field is a plain string (empty when unset). */
    public record ProfileInfoView(
            String displayName, String username, String headline, String company, String location,
            String school, String website, String github, String linkedin, List<String> tags) {}

    static final int MAX_TAGS = 8;
    private static final Pattern HANDLE = Pattern.compile("[A-Za-z0-9_.-]*");

    private final ProfileInfoRepository repository;

    public ProfileInfoService(ProfileInfoRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public ProfileInfoView get(UUID clientId) {
        return repository.findById(clientId).map(ProfileInfoService::toView).orElseGet(ProfileInfoService::empty);
    }

    @Transactional
    public ProfileInfoView update(UUID clientId, ProfileInfoView request) {
        ProfileInfo info = repository.findById(clientId).orElseGet(() -> new ProfileInfo(clientId));
        String username = handle("Username", request.username(), 30);
        if (!username.isEmpty() && repository.existsByUsernameIgnoreCaseAndClientIdNot(username, clientId)) {
            throw new IllegalArgumentException("That username is taken");
        }
        info.apply(
                text("Display name", request.displayName(), 40),
                username,
                text("Headline", request.headline(), 120),
                text("Company", request.company(), 60),
                text("Location", request.location(), 60),
                text("School", request.school(), 60),
                website(request.website()),
                handle("GitHub", request.github(), 60),
                handle("LinkedIn", request.linkedin(), 60),
                String.join(",", tags(request.tags())));
        return toView(repository.save(info));
    }

    private static ProfileInfoView empty() {
        return new ProfileInfoView("", "", "", "", "", "", "", "", "", List.of());
    }

    private static ProfileInfoView toView(ProfileInfo info) {
        List<String> tags = info.getTags().isBlank() ? List.of() : Arrays.asList(info.getTags().split(","));
        return new ProfileInfoView(
                info.getDisplayName(), info.getUsername(), info.getHeadline(), info.getCompany(), info.getLocation(),
                info.getSchool(), info.getWebsite(), info.getGithub(), info.getLinkedin(), tags);
    }

    static String text(String field, String value, int max) {
        String trimmed = value == null ? "" : value.trim();
        if (trimmed.length() > max) {
            throw new IllegalArgumentException(field + " must be at most " + max + " characters");
        }
        return trimmed;
    }

    static String handle(String field, String value, int max) {
        String trimmed = text(field, value, max);
        if (!HANDLE.matcher(trimmed).matches()) {
            throw new IllegalArgumentException(field + " may only contain letters, digits, '.', '_' and '-'");
        }
        return trimmed;
    }

    static String website(String value) {
        String trimmed = text("Website", value, 120);
        if (!trimmed.isEmpty() && !trimmed.startsWith("https://") && !trimmed.startsWith("http://")) {
            throw new IllegalArgumentException("Website must start with http:// or https://");
        }
        return trimmed;
    }

    static List<String> tags(List<String> values) {
        if (values == null) {
            return List.of();
        }
        LinkedHashSet<String> clean = new LinkedHashSet<>();
        for (String value : values) {
            String tag = text("Tag", value, 20);
            if (tag.contains(",")) {
                throw new IllegalArgumentException("Tags cannot contain commas");
            }
            if (!tag.isEmpty()) {
                clean.add(tag);
            }
        }
        if (clean.size() > MAX_TAGS) {
            throw new IllegalArgumentException("At most " + MAX_TAGS + " tags");
        }
        return List.copyOf(clean);
    }
}
