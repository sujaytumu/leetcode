import assert from "node:assert/strict";
import { test } from "node:test";
import { buildBackup, isBackupKey, parseBackup } from "../lib/backup.ts";

const fake = (o: Record<string, string>) => {
  const keys = Object.keys(o);
  return { length: keys.length, key: (i: number) => keys[i] ?? null, getItem: (k: string) => o[k] ?? null };
};

test("backup includes app data but never credentials or caches", () => {
  const b = buildBackup(fake({ "lc-review": "{}", "lc-times": "{}", "lc-auth-token": "secret", "lc-client-id": "x", "lc-cache:/api/a": "1", other: "z" }));
  assert.deepEqual(Object.keys(b.data).sort(), ["lc-review", "lc-times"]);
});

test("restore accepts a valid backup and drops blocked or foreign keys", () => {
  const text = JSON.stringify({ app: "leetcode-practice", version: 1, exportedAt: "", data: { "lc-review": "{}", "lc-auth-token": "evil", foo: "bar", "lc-times": 5 } });
  assert.deepEqual(parseBackup(text), { "lc-review": "{}" });
});

test("restore rejects wrong files with readable errors", () => {
  assert.throws(() => parseBackup("nope"), /valid JSON/);
  assert.throws(() => parseBackup("{}"), /not a LeetCode Practice backup/);
  assert.throws(() => parseBackup(JSON.stringify({ app: "leetcode-practice", version: 1, data: { "lc-auth-token": "x" } })), /nothing to restore/);
});

test("key filter", () => {
  assert.ok(isBackupKey("lc-draft2:two-sum:java"));
  assert.ok(!isBackupKey("lc-auth-token"));
});
