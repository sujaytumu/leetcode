import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";

// Minimal in-memory localStorage for the modules under test.
const mem = new Map<string, string>();
(globalThis as unknown as { localStorage: Storage }).localStorage = {
  getItem: (k: string) => mem.get(k) ?? null,
  setItem: (k: string, v: string) => void mem.set(k, v),
  removeItem: (k: string) => void mem.delete(k),
  clear: () => mem.clear(), key: () => null, length: 0,
} as Storage;

const { dueAt, loadReviews, markReviewed, STEPS, daysUntil } = await import("../lib/review.ts");
const { recordTime, getTime, fmtSecs } = await import("../lib/times.ts");
const DAY = 86400000;

beforeEach(() => mem.clear());

test("first review is due one day after the first solve", () => {
  const solved = "2026-01-01T00:00:00.000Z";
  assert.equal(dueAt(solved), new Date(solved).getTime() + STEPS[0] * DAY);
});

test("remembering moves to longer intervals and caps at the last step", () => {
  const solved = "2026-01-01T00:00:00.000Z";
  for (let i = 0; i < 10; i++) markReviewed("two-sum", true, solved);
  assert.equal(loadReviews()["two-sum"].stage, STEPS.length - 1);
});

test("forgetting restarts the schedule", () => {
  markReviewed("two-sum", true, "x"); markReviewed("two-sum", true, "x");
  assert.equal(loadReviews()["two-sum"].stage, 2);
  markReviewed("two-sum", false, "x");
  assert.equal(loadReviews()["two-sum"].stage, 0);
});

test("daysUntil rounds up partial days", () => {
  assert.equal(daysUntil(1000 + DAY / 2, 1000), 1);
  assert.equal(daysUntil(1000 + 3 * DAY, 1000), 3);
});

test("solve times keep the best and count runs", () => {
  assert.equal(getTime("two-sum"), null);
  assert.equal(recordTime("two-sum", 600).improved, false);
  const second = recordTime("two-sum", 420);
  assert.equal(second.improved, true);
  const third = recordTime("two-sum", 500);
  assert.deepEqual(third.rec, { best: 420, last: 500, runs: 3 });
  assert.equal(third.improved, false);
});

test("fmtSecs formats minutes and seconds", () => {
  assert.equal(fmtSecs(65), "01:05");
  assert.equal(fmtSecs(3600), "60:00");
});
