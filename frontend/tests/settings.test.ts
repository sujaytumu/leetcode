import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanGithub, cleanWebsite, normalizeField } from "../lib/settingsFields.ts";

test("github accepts usernames and urls", () => {
  assert.equal(cleanGithub("sujaytumu"), "sujaytumu");
  assert.equal(cleanGithub("@sujaytumu"), "sujaytumu");
  assert.equal(cleanGithub("https://github.com/sujaytumu/"), "sujaytumu");
  assert.equal(cleanGithub("github.com/a-b?tab=repos"), "a-b");
  assert.equal(cleanGithub(""), "");
  assert.equal(cleanGithub("not valid!"), null);
});
test("website gets a scheme and must look like a host", () => {
  assert.equal(cleanWebsite("example.com"), "https://example.com");
  assert.equal(cleanWebsite("http://a.io/x"), "http://a.io/x");
  assert.equal(cleanWebsite("localhost"), null);
  assert.equal(cleanWebsite(""), "");
});
test("normalizeField enforces limits and required fields", () => {
  assert.ok(normalizeField("displayName", "  ").error);
  assert.equal(normalizeField("displayName", " Sam ").value, "Sam");
  assert.ok(normalizeField("headline", "x".repeat(201)).error);
  assert.ok(normalizeField("username", "a b").error);
  assert.equal(normalizeField("username", "sam_01").value, "sam_01");
});

import { cleanLinkedin } from "../lib/settingsFields.ts";
test("cleanLinkedin accepts a pasted profile URL", () => {
  assert.equal(cleanLinkedin("https://www.linkedin.com/in/tumu-sujay-babu-8633b0274/"), "tumu-sujay-babu-8633b0274");
  assert.equal(cleanLinkedin("linkedin.com/in/abc"), "abc");
  assert.equal(cleanLinkedin("@abc"), "abc");
  assert.equal(cleanLinkedin(""), "");
  assert.equal(cleanLinkedin("bad name!"), null);
});
