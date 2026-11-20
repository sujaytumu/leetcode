import assert from "node:assert/strict";
import { test } from "node:test";
import { ACCENTS, accentByKey, applyAccent } from "../lib/appearance.ts";

test("every accent has valid hex colours and a unique key", () => {
  const hex = /^#[0-9a-f]{6}$/i;
  for (const a of ACCENTS) { assert.match(a.dark, hex); assert.match(a.light, hex); }
  assert.equal(new Set(ACCENTS.map((a) => a.key)).size, ACCENTS.length);
});

test("lookup ignores unknown keys", () => {
  assert.equal(accentByKey("blue")?.key, "blue");
  assert.equal(accentByKey("nope"), null);
  assert.equal(accentByKey(null), null);
});

test("applyAccent sets and clears the CSS variables", () => {
  const props = new Map<string, string>();
  const root = { style: { setProperty: (k: string, v: string) => void props.set(k, v), removeProperty: (k: string) => void props.delete(k) } } as unknown as HTMLElement;
  applyAccent(accentByKey("green"), root);
  assert.equal(props.get("--accent-d"), "#3ddc84");
  assert.equal(props.get("--accent-l"), "#1f9d55");
  applyAccent(null, root);
  assert.equal(props.size, 0);
});
