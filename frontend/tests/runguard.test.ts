import test from "node:test";
import assert from "node:assert/strict";
import { initialLang, runBlocker, MAX_SOURCE_CHARS } from "../lib/runguard.ts";

test("initialLang prefers the link, then the saved choice, then C++", () => {
  assert.equal(initialLang("java", "python"), "java");
  assert.equal(initialLang(null, "python"), "python");
  assert.equal(initialLang("c++", "bogus"), "cpp");
  assert.equal(initialLang(null, null), "cpp");
});

test("runBlocker stops requests the server would answer with 400", () => {
  assert.match(runBlocker("", "int x;")!, /language/i);
  assert.match(runBlocker("cpp", "   \n")!, /empty/i);
  assert.match(runBlocker("cpp", "x".repeat(MAX_SOURCE_CHARS + 1))!, /too long/i);
  assert.equal(runBlocker("cpp", "x".repeat(MAX_SOURCE_CHARS)), null);
  assert.equal(runBlocker("python", "print(1)"), null);
});
