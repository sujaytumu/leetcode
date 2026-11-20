import assert from "node:assert/strict";
import { test } from "node:test";
import { timeAgo } from "../lib/timeago.ts";

const now = Date.UTC(2026, 10, 20, 12, 0, 0);
const ago = (s: number) => timeAgo(now - s * 1000, now, "en");

test("recent times", () => {
  assert.equal(ago(10), "just now");
  assert.equal(ago(60), "1 minute ago");
  assert.equal(ago(5 * 60), "5 minutes ago");
  assert.equal(ago(3 * 3600), "3 hours ago");
});
test("days, weeks, months, years", () => {
  assert.equal(ago(86400), "1 day ago");
  assert.equal(ago(3 * 86400), "3 days ago");
  assert.equal(ago(14 * 86400), "2 weeks ago");
  assert.equal(ago(70 * 86400), "2 months ago");
  assert.equal(ago(800 * 86400), "2 years ago");
});
test("invalid dates give an empty string", () => {
  assert.equal(timeAgo("not a date", now, "en"), "");
});
