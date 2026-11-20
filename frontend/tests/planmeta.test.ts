import assert from "node:assert/strict";
import { test } from "node:test";
import { bannerFor, planLevel, planState } from "../lib/planMeta.ts";

const mk = (e: number, m: number, h: number) => [
  ...Array(e).fill({ difficulty: "EASY" }), ...Array(m).fill({ difficulty: "MEDIUM" }), ...Array(h).fill({ difficulty: "HARD" }),
];

test("level follows the difficulty mix", () => {
  assert.equal(planLevel(mk(8, 2, 0)), "Beginner");
  assert.equal(planLevel(mk(3, 6, 1)), "Intermediate");
  assert.equal(planLevel(mk(2, 4, 4)), "Advanced");
  assert.equal(planLevel([]), "Beginner");
});
test("banner is stable per id", () => {
  assert.deepEqual(bannerFor("top-interview"), bannerFor("top-interview"));
  assert.equal(bannerFor("x").length, 2);
});
test("plan state", () => {
  assert.equal(planState({ solved: 0, total: 10 }), "start");
  assert.equal(planState({ solved: 3, total: 10 }), "continue");
  assert.equal(planState({ solved: 10, total: 10 }), "done");
});
