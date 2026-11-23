import assert from "node:assert/strict";
import { test } from "node:test";
import { dayKey as key, weekTotal } from "../lib/weekly.ts";

test("weekTotal counts the seven days ending on the given day", () => {
  const end = new Date(2026, 10, 18);
  const day = (offset: number) => { const d = new Date(end); d.setDate(d.getDate() - offset); return key(d); };
  const cal = [{ date: day(0), count: 2 }, { date: day(6), count: 3 }, { date: day(7), count: 5 }, { date: day(-1), count: 9 }];
  assert.equal(weekTotal(cal, end), 5);
});
