import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { formatInput, formatInputParts, formatOutput } from "../lib/example.ts";

const TWO_SUM = `import sys

def solve(nums, target):
    pass

def main():
    lines = sys.stdin.read().splitlines()
    pos = 0
    nums_len = int(lines[pos]); pos += 1
    nums = list(map(int, lines[pos].split())) if nums_len > 0 else []; pos += 1
    target = int(lines[pos]); pos += 1
    result = solve(nums, target)
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
`;

test("named arguments and list output, as on LeetCode", () => {
  assert.equal(formatInput(TWO_SUM, "4\n2 7 11 15\n9\n"), "nums = [2,7,11,15], target = 9");
  assert.equal(formatOutput(TWO_SUM, "0 1\n"), "[0,1]");
  assert.equal(formatInput(TWO_SUM, "0\n\n5\n"), "nums = [], target = 5");
  assert.equal(formatOutput(TWO_SUM, "\n"), "[]");
});

test("arguments are also available as name/value pairs", () => {
  assert.deepEqual(formatInputParts(TWO_SUM, "4\n2 7 11 15\n9\n"), [
    { name: "nums", value: "[2,7,11,15]" },
    { name: "target", value: "9" },
  ]);
});

test("unknown layouts fall back to null instead of guessing", () => {
  assert.equal(formatInput("def main():\n    x = 1\n\nif __name__", "1"), null);
  assert.equal(formatInput("no main here", "1"), null);
});

// Every sample of every seeded problem must format, so no problem silently keeps the raw display.
test("every seeded problem's samples format", () => {
  const url = new URL("../../backend/src/main/resources/seed/problems.json", import.meta.url);
  const problems = JSON.parse(readFileSync(url, "utf8")) as { slug: string; starterCode: Record<string, string>; testCases: { sample?: boolean; input: string; expectedOutput: string }[] }[];
  const failures: string[] = [];
  let checked = 0;
  for (const p of problems) {
    for (const t of p.testCases.filter((c) => c.sample)) {
      checked++;
      const i = formatInput(p.starterCode.python, t.input);
      const o = formatOutput(p.starterCode.python, t.expectedOutput);
      if (i === null || o === null) failures.push(`${p.slug}: input=${i} output=${o}`);
    }
  }
  assert.ok(checked > 100, `only checked ${checked} samples`);
  assert.deepEqual(failures, []);
});
