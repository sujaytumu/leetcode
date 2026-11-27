import test from "node:test";
import assert from "node:assert/strict";
import { topicOf, compareTopics } from "../lib/sheets.ts";

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
