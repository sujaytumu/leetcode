import test from "node:test";
import assert from "node:assert/strict";
import { isClientId, failureMessage } from "../lib/apierr.ts";

test("only real UUIDs count as client ids", () => {
  assert.equal(isClientId("3f2504e0-4f89-11d3-9a0c-0305e82c3301"), true);
  assert.equal(isClientId("3F2504E0-4F89-41D3-9A0C-0305E82C3301"), true);
  for (const bad of ["", null, undefined, "abc", "user-123", "3f2504e0-4f89-11d3-9a0c-0305e82c330", "3f2504e04f8911d39a0c0305e82c3301"]) assert.equal(isClientId(bad), false);
});

test("a 400 names the endpoint, other failures stay as they were", () => {
  assert.equal(failureMessage(400, "Unsupported language.", "/api/problems/two-sum/submit?x=1"), "Unsupported language (HTTP 400 on /api/problems/two-sum/submit)");
  assert.equal(failureMessage(400, "", "/api/plans"), "The server rejected the request (HTTP 400 on /api/plans)");
  assert.equal(failureMessage(503, "", "/api/x"), "The server is starting up.");
  assert.equal(failureMessage(404, "Problem not found: x", "/api/problems/x"), "Problem not found: x");
  assert.equal(failureMessage(500, "", "/api/x"), "Request failed (HTTP 500).");
});
