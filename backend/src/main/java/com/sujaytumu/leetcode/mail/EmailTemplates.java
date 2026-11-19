package com.sujaytumu.leetcode.mail;

import com.sujaytumu.leetcode.problem.Difficulty;

/** Plain, table-free HTML that renders the same everywhere, plus a text alternative for each message. */
public final class EmailTemplates {

    private EmailTemplates() {}

    public static EmailSender.Message passwordReset(String to, String link, int minutes) {
        String text = "Someone asked to reset the password for your LeetCode Practice account.\n\n"
                + "Open this link within " + minutes + " minutes to choose a new password:\n" + link + "\n\n"
                + "If this was not you, ignore this email. Your password stays the same.";
        String html = shell("Reset your password",
                "<p>Someone asked to reset the password for your LeetCode Practice account.</p>"
                        + button(link, "Choose a new password")
                        + "<p style=\"color:#666;font-size:13px\">The link works for " + minutes
                        + " minutes and only once. If this was not you, ignore this email. Your password stays the same.</p>");
        return new EmailSender.Message(to, "Reset your LeetCode Practice password", html, text, null);
    }

    public static EmailSender.Message dailyProblem(
            String to, String title, Difficulty difficulty, String problemLink, String unsubscribeLink) {
        String level = difficulty == null ? "" : difficulty.name().charAt(0) + difficulty.name().substring(1).toLowerCase();
        String text = "Today's problem: " + title + (level.isEmpty() ? "" : " (" + level + ")") + "\n\n"
                + "Solve it: " + problemLink + "\n\n"
                + "Stop these emails: " + unsubscribeLink;
        String html = shell("Today's problem",
                "<p style=\"font-size:18px;margin:0 0 4px\"><b>" + esc(title) + "</b></p>"
                        + (level.isEmpty() ? "" : "<p style=\"margin:0 0 12px;color:#666\">" + esc(level) + "</p>")
                        + button(problemLink, "Solve it now")
                        + "<p style=\"color:#666;font-size:12px\"><a href=\"" + esc(unsubscribeLink) + "\">Unsubscribe</a> from the daily email.</p>");
        return new EmailSender.Message(to, "Daily problem: " + title, html, text, unsubscribeLink);
    }

    private static String shell(String heading, String body) {
        return "<div style=\"font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:480px;margin:0 auto;padding:16px;color:#222\">"
                + "<h2 style=\"margin:0 0 12px\">" + esc(heading) + "</h2>" + body + "</div>";
    }

    private static String button(String href, String label) {
        return "<p><a href=\"" + esc(href) + "\" style=\"display:inline-block;background:#f59e0b;color:#111;"
                + "padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600\">" + esc(label) + "</a></p>"
                + "<p style=\"color:#666;font-size:12px;word-break:break-all\">" + esc(href) + "</p>";
    }

    static String esc(String s) {
        return s == null ? "" : s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
    }
}
