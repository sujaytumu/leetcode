import test from "node:test";
import assert from "node:assert/strict";
import { topicOf, compareTopics, sheetFromParam, sheetsOf, isSheetTag } from "../lib/sheets.ts";

test("topicOf picks the most specific tag", () => {
  assert.equal(topicOf({ tags: ["array", "backtracking", "striver-a2z"] }), "backtracking");
  assert.equal(topicOf({ tags: ["array", "binary-search", "striver-sde"] }), "binary-search");
  assert.equal(topicOf({ tags: ["tree", "bst", "striver-sde"] }), "tree");
  assert.equal(topicOf({ tags: ["array", "hash-table", "striver-sde"] }), "array");
  assert.equal(topicOf({ tags: ["sorting", "striver-sde"] }), "sorting");
  assert.equal(topicOf({ tags: ["striver-sde"] }), "other");
});

test("topics sort in the fixed sheet order, unknown ones last", () => {
  const sorted = ["graph", "other", "array", "dynamic-programming", "string", "backtracking"].sort(compareTopics);
  assert.deepEqual(sorted, ["array", "string", "backtracking", "graph", "dynamic-programming", "other"]);
});

test("Magic 50 is a third sheet with its own pill and links", () => {
  assert.equal(sheetFromParam("m50")?.tag, "magic-50");
  assert.equal(sheetFromParam("magic50")?.tag, "magic-50");
  assert.equal(sheetFromParam("magic-50")?.short, "M50");
  assert.equal(isSheetTag("magic-50"), true);
  assert.deepEqual(sheetsOf(["array", "striver-a2z", "magic-50"]).map((s) => s.short), ["A2Z", "M50"]);
  assert.equal(topicOf({ tags: ["array", "dynamic-programming", "magic-50"] }), "dynamic-programming");
});
