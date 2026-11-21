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

test("LeetCode-style `class Solution` code gets a forwarding solve in C++, Java and Python", () => {
  const two = problems.find((p) => p.slug === "two-sum")!;
  const cpp = composeProgram(splitTemplate(two.starterCode.cpp, "cpp")!,
    "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        return {0, 1};\n    }\n};\n");
  assert.match(cpp, /vector<int> solve\(vector<int> nums, int target\) \{ return Solution\(\)\.twoSum\(nums, target\); \}/);
  const java = composeProgram(splitTemplate(two.starterCode.java, "java")!,
    "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        return new int[0];\n    }\n}\n");
  assert.match(java, /static class Solution/);
  assert.match(java, /static int\[\] solve\(int\[\] nums, int target\) \{ return new Solution\(\)\.twoSum\(nums, target\); \}/);
  const py = composeProgram(splitTemplate(two.starterCode.python, "python")!,
    "class Solution:\n    def twoSum(self, nums, target):\n        return [0, 1]\n");
  assert.match(py, /def solve\(\*args\):\n    r = Solution\(\)\.twoSum\(\*args\)\n    return r\n/);
  // Code that already defines solve is left alone.
  const plain = splitTemplate(two.starterCode.cpp, "cpp")!;
  assert.ok(!composeProgram(plain, plain.stub).includes("Solution()"));
});

test("buildInput is the inverse of formatInputParts for every sample that formats", async () => {
  const { buildInput, formatInputParts } = await import("../lib/example.ts");
  const full = JSON.parse(readFileSync(new URL("../public/problems-snapshot.json", import.meta.url), "utf8")) as (Snap & { samples: { input: string }[] })[];
  let checked = 0;
  for (const p of full) {
    for (const s of p.samples) {
      const parts = formatInputParts(p.starterCode.python, s.input);
      if (!parts) continue;
      const back = buildInput(p.starterCode.python, parts);
      assert.ok(back !== null, `${p.slug} should rebuild`);
      assert.deepEqual(formatInputParts(p.starterCode.python, back!), parts, p.slug);
      checked++;
    }
  }
  assert.ok(checked > 150, `only ${checked} samples checked`);
});
