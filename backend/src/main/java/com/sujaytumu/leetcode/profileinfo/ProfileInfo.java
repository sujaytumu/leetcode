package com.sujaytumu.leetcode.profileinfo;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

/** The editable "about me" card of one client, like the left column of a LeetCode profile. */
@Entity
@Table(name = "profile_info")
public class ProfileInfo {

    @Id
    @Column(name = "client_id")
    private UUID clientId;

    @Column(name = "display_name", length = 40, nullable = false)
    private String displayName = "";

    @Column(name = "username", length = 30, nullable = false)
    private String username = "";

    @Column(name = "headline", length = 120, nullable = false)
    private String headline = "";

    @Column(name = "company", length = 60, nullable = false)
    private String company = "";

    @Column(name = "location", length = 60, nullable = false)
    private String location = "";

    @Column(name = "school", length = 60, nullable = false)
    private String school = "";

    @Column(name = "website", length = 120, nullable = false)
    private String website = "";

    @Column(name = "github", length = 60, nullable = false)
    private String github = "";

    @Column(name = "linkedin", length = 60, nullable = false)
    private String linkedin = "";

    /** Comma separated; each tag is already validated to contain no comma. */
    @Column(name = "tags", length = 300, nullable = false)
    private String tags = "";

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    protected ProfileInfo() {}

    public ProfileInfo(UUID clientId) {
        this.clientId = clientId;
    }

    public String getDisplayName() { return displayName; }
    public String getUsername() { return username; }
    public String getHeadline() { return headline; }
    public String getCompany() { return company; }
    public String getLocation() { return location; }
    public String getSchool() { return school; }
    public String getWebsite() { return website; }
    public String getGithub() { return github; }
    public String getLinkedin() { return linkedin; }
    public String getTags() { return tags; }

    public void apply(
            String displayName, String username, String headline, String company, String location,
            String school, String website, String github, String linkedin, String tags) {
        this.displayName = displayName;
        this.username = username;
        this.headline = headline;
        this.company = company;
        this.location = location;
        this.school = school;
        this.website = website;
        this.github = github;
        this.linkedin = linkedin;
        this.tags = tags;
        this.updatedAt = Instant.now();
    }
}
