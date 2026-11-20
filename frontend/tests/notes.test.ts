import assert from "node:assert/strict";
import { test } from "node:test";
import { filterNotes, listNotes, toMarkdown } from "../lib/notes.ts";

const fake = (o: Record<string, string>) => {
  const keys = Object.keys(o);
  return { length: keys.length, key: (i: number) => keys[i] ?? null, getItem: (k: string) => o[k] ?? null };
};
const store = fake({
  "lc-notes:two-sum": "Use a hash map", "lc-notes-ts:two-sum": "200",
  "lc-notes:lru-cache": "Doubly linked list + map", "lc-notes-ts:lru-cache": "300",
  "lc-notes:empty": "   ", "lc-draft:x": "ignored",
});
const titles = new Map([["two-sum", "Two Sum"], ["lru-cache", "LRU Cache"]]);

test("lists non-empty notes newest first", () => {
  assert.deepEqual(listNotes(store).map((n) => n.slug), ["lru-cache", "two-sum"]);
});
test("filters by text, title or slug", () => {
  const all = listNotes(store);
  assert.deepEqual(filterNotes(all, "hash", titles).map((n) => n.slug), ["two-sum"]);
  assert.deepEqual(filterNotes(all, "lru", titles).map((n) => n.slug), ["lru-cache"]);
  assert.equal(filterNotes(all, "", titles).length, 2);
});
test("exports markdown with titles", () => {
  assert.match(toMarkdown(listNotes(store), titles), /## LRU Cache\n\nDoubly linked list \+ map\n/);
});
