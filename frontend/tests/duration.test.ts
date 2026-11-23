import assert from "node:assert/strict";
import { test } from "node:test";
import { splitDuration } from "../lib/duration.ts";

test("splits seconds into days, hours, minutes, seconds", () => {
  assert.deepEqual(splitDuration(90061), { days: 1, hours: 1, minutes: 1, seconds: 1 });
  assert.deepEqual(splitDuration(59), { days: 0, hours: 0, minutes: 0, seconds: 59 });
});
test("negative and invalid values show zero", () => {
  assert.deepEqual(splitDuration(-5), { days: 0, hours: 0, minutes: 0, seconds: 0 });
  assert.deepEqual(splitDuration(NaN), { days: 0, hours: 0, minutes: 0, seconds: 0 });
});
