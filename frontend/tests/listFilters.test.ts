import assert from "node:assert/strict";
import { test } from "node:test";
import { parseFilters } from "../lib/listFilters.ts";

test("parseFilters keeps valid saved filters", () => {
  const f = parseFilters(JSON.stringify({ difficulty: "HARD", tag: "graph", status: "TODO", sort: "acceptance", dir: "desc", bookmarked: true }));
  assert.deepEqual(f, { difficulty: "HARD", tag: "graph", status: "TODO", sort: "acceptance", dir: "desc", bookmarked: true });
});

test("parseFilters ignores missing, malformed and unexpected values", () => {
  assert.deepEqual(parseFilters(null), {});
  assert.deepEqual(parseFilters("not json"), {});
  assert.deepEqual(parseFilters("[1,2]"), {});
  assert.deepEqual(parseFilters(JSON.stringify({ difficulty: "IMPOSSIBLE", sort: "drop table", dir: "sideways", bookmarked: "yes", tag: 5 })), {});
  assert.deepEqual(parseFilters(JSON.stringify({ tag: "x".repeat(41) })), {});
});
