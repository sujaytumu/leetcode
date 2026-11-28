import test from "node:test";
import assert from "node:assert/strict";
import { canGoBack, position, trackPositions } from "../lib/nav.ts";

type Hist = { state: Record<string, unknown> | null; pushState: (s: unknown, t: string, u?: string) => void; replaceState: (s: unknown, t: string, u?: string) => void };
const fakeWindow = (state: Record<string, unknown> | null) => {
  const h: Hist = { state, pushState(s) { h.state = s as Record<string, unknown>; }, replaceState(s) { h.state = s as Record<string, unknown>; } };
  (globalThis as unknown as { window: unknown }).window = { history: h };
  return h;
};

test("the first screen of a visit has nothing earlier to go back to", () => {
  fakeWindow(null);
  assert.equal(position(), 0);
  assert.equal(canGoBack(), false);
});

test("every push stamps the next position, replace keeps it, so Back knows an earlier app page exists", () => {
  const h = fakeWindow({ __NA: true });
  trackPositions();
  h.pushState({ __NA: true }, "", "/problems/two-sum");
  assert.equal(position(), 1);
  assert.equal(canGoBack(), true);
  h.replaceState({ __NA: true }, "", "/problems/two-sum?x=1");
  assert.equal(position(), 1);
  h.pushState({ lcOverlay: "x" }, "", "/problems/two-sum");
  assert.equal(position(), 2);
  assert.equal(h.state?.lcOverlay, "x"); // other state is kept
});
