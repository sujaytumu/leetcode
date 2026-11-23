import assert from "node:assert/strict";
import { test } from "node:test";
import { cardData } from "../lib/shareCard.ts";
import type { Profile } from "../lib/api.ts";

const base = {
  progress: { total: 205, solved: 12, attempted: 3, bookmarked: 0, byDifficulty: { EASY: { total: 60, solved: 8 }, MEDIUM: { total: 100, solved: 4 } } },
  currentStreak: 3, maxStreak: 9, activeDays: 20,
  skills: [{ tag: "dp", solved: 1 }, { tag: "array", solved: 6 }, { tag: "graph", solved: 3 }, { tag: "tree", solved: 2 }],
} as unknown as Profile;

test("card data summarises the profile", () => {
  const c = cardData(base, "Sam");
  assert.equal(c.solved, 12); assert.equal(c.total, 205);
  assert.deepEqual(c.easy, [8, 60]); assert.deepEqual(c.medium, [4, 100]);
  assert.deepEqual(c.hard, [0, 0]); // missing difficulty counts as zero
  assert.deepEqual(c.topSkills, ["array", "graph", "tree"]);
  assert.equal(c.name, "Sam");
});

test("empty name falls back to a neutral label", () => {
  assert.equal(cardData(base, "").name, "Anonymous coder");
});
