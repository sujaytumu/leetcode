import assert from "node:assert/strict";
import { test } from "node:test";
import { formatBirthday, validBirthday } from "../lib/localProfile.ts";

test("birthday formats like LeetCode shows it", () => {
  assert.equal(formatBirthday("2004-12-14"), "December 14, 2004");
  assert.equal(formatBirthday("2004-02-31"), "");
  assert.equal(formatBirthday("nope"), "");
});
test("birthday validation", () => {
  const now = new Date(2026, 10, 22);
  assert.ok(validBirthday("2004-12-14", now));
  assert.ok(!validBirthday("2030-01-01", now));
  assert.ok(!validBirthday("1800-01-01", now));
  assert.ok(!validBirthday("", now));
});
