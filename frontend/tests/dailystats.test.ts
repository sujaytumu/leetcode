import assert from "node:assert/strict";
import { test } from "node:test";
import { dailyStreak } from "../lib/dailyStats.ts";

const d = (date: string, solved = true) => ({ date, solved });

test("streak counts consecutive solved days ending today", () => {
  assert.equal(dailyStreak([d("2026-11-18"), d("2026-11-19"), d("2026-11-20")], "2026-11-20"), 3);
});
test("an unsolved today does not break yesterday's streak", () => {
  assert.equal(dailyStreak([d("2026-11-18"), d("2026-11-19"), d("2026-11-20", false)], "2026-11-20"), 2);
});
test("a gap ends the streak", () => {
  assert.equal(dailyStreak([d("2026-11-17"), d("2026-11-19"), d("2026-11-20")], "2026-11-20"), 2);
  assert.equal(dailyStreak([d("2026-11-10")], "2026-11-20"), 0);
});
test("streak crosses a month boundary when the days are present", () => {
  assert.equal(dailyStreak([d("2026-10-31"), d("2026-11-01")], "2026-11-01"), 2);
});
