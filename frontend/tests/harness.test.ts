import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { composeProgram, extractUser, shiftErrorLines, splitTemplate } from "../lib/harness.ts";

interface Snap { slug: string; starterCode: Record<string, string> }
const problems = JSON.parse(readFileSync(new URL("../public/problems-snapshot.json", import.meta.url), "utf8")) as Snap[];
const LANGS = ["python", "java", "cpp", "javascript"];

test("every bundled starter template splits in every language", () => {
  assert.ok(problems.length > 100);
  for (const p of problems) {
    for (const lang of LANGS) {
      const t = p.starterCode[lang];
      if (t === undefined) continue;
      assert.ok(splitTemplate(t, lang), `${p.slug} (${lang}) should split`);
    }
  }
});

test("compose then extract gives back exactly the user's code", () => {
  for (const p of problems) {
    for (const lang of LANGS) {
      const t = p.starterCode[lang];
      if (t === undefined) continue;
      const parts = splitTemplate(t, lang)!;
      const full = composeProgram(parts, parts.stub);
      assert.equal(extractUser(full, lang), parts.stub.replace(/\s+$/, ""), `${p.slug} (${lang})`);
    }
  }
});

test("composing the untouched stub keeps the hidden prefix and suffix intact", () => {
  const p = problems[0], parts = splitTemplate(p.starterCode.python, "python")!;
  const full = composeProgram(parts, "def solve(x):\n    return 1");
  assert.ok(full.startsWith(parts.prefix));
  assert.ok(full.endsWith(parts.suffix));
  assert.ok(full.includes("def solve(x):\n    return 1"));
});

test("extractUser returns null when there are no markers", () => {
  assert.equal(extractUser("print('hi')", "python"), null);
});

test("unrecognised templates are not split", () => {
  assert.equal(splitTemplate("no function here", "python"), null);
  assert.equal(splitTemplate("whatever", "rust"), null);
});

test("error line numbers are shifted to the user's code", () => {
  const parts = { prefix: "a\nb\nc\n", stub: "", suffix: "", lang: "python" }; // 4 prefix lines incl. the marker line
  assert.equal(shiftErrorLines('File "main.py:10"', parts), 'File "main.py:6"');
  assert.equal(shiftErrorLines("error at line 2", parts), "error at line 2"); // inside the hidden part: left alone
  assert.equal(shiftErrorLines("Main.java:9: error", parts), "Main.java:5: error");
});
