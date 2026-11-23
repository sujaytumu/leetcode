import test from "node:test";
import assert from "node:assert/strict";

const mem = new Map<string, string>();
(globalThis as any).localStorage = {
  getItem: (k: string) => mem.get(k) ?? null,
  setItem: (k: string, v: string) => void mem.set(k, v),
};
const { getRecent, pushRecent, RECENT_MAX } = await import("../lib/recent.ts");

test("newest first and de-duplicated", () => {
  mem.clear();
  pushRecent({ slug: "a", title: "A" });
  pushRecent({ slug: "b", title: "B" });
  const r = pushRecent({ slug: "a", title: "A" });
  assert.deepEqual(r.map((x) => x.slug), ["a", "b"]);
});

test("capped at RECENT_MAX", () => {
  mem.clear();
  for (let i = 0; i < RECENT_MAX + 5; i++) pushRecent({ slug: `s${i}`, title: `T${i}` });
  assert.equal(getRecent().length, RECENT_MAX);
  assert.equal(getRecent()[0].slug, `s${RECENT_MAX + 4}`);
});

test("corrupt storage yields empty list", () => {
  mem.set("lc-recent", "{oops");
  assert.deepEqual(getRecent(), []);
});
