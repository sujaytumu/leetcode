import assert from "node:assert/strict";
import { test } from "node:test";
import { diffLines } from "../lib/diff.ts";

const tag = (a: string, b: string) => diffLines(a, b).map((l) => `${l.kind[0]}:${l.text}`);

test("identical text has only unchanged lines", () => {
  assert.deepEqual(tag("a\nb", "a\nb"), ["s:a", "s:b"]);
});
test("a replaced line shows as removed then added", () => {
  assert.deepEqual(tag("a\nb\nc", "a\nx\nc"), ["s:a", "d:b", "a:x", "s:c"]);
});
test("insertions and deletions at the ends", () => {
  assert.deepEqual(tag("a\nb\nc", "a\nc\nd"), ["s:a", "d:b", "s:c", "a:d"]);
});
test("Windows line endings are treated like Unix ones", () => {
  assert.deepEqual(tag("a\r\nb", "a\nb"), ["s:a", "s:b"]);
});
test("diff of a long file stays correct", () => {
  const a = Array.from({ length: 300 }, (_, i) => `line ${i}`).join("\n");
  const b = a.replace("line 150", "changed");
  const d = diffLines(a, b);
  assert.equal(d.filter((l) => l.kind === "add").length, 1);
  assert.equal(d.filter((l) => l.kind === "del").length, 1);
});
