#!/usr/bin/env node
// Rewrites the C++ answers in seed/solutions.json from the judge's `solve(...)` form into the form LeetCode shows:
//   class Solution { public: R method(args) { ... } };
// using the method name and parameter list from the editor's own stub (frontend/lib/harness.ts), so the Solutions tab
// and the editor agree. Helpers stay above the class. Run after scripts/build-solutions.js, then check with
// scripts/verify-paste.mjs (compiles every answer through the editor path and runs all test cases).
//   node --experimental-strip-types scripts/lc-style-cpp.mjs [--out file.json]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { splitTemplate } from "../frontend/lib/harness.ts";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const SEED = path.join(ROOT, "backend/src/main/resources/seed/");
const outArg = process.argv.indexOf("--out");
const outFile = outArg >= 0 ? process.argv[outArg + 1] : SEED + "solutions.json";
const solutions = JSON.parse(fs.readFileSync(SEED + "solutions.json", "utf8"));
const problems = Object.fromEntries(JSON.parse(fs.readFileSync(SEED + "problems.json", "utf8")).map((p) => [p.slug, p]));

const SOLVE = /^[A-Za-z_].*\bsolve\(.*\)\s*\{\s*$/;
const paramNames = (list) => {
  const out = []; let d = 0, cur = "";
  for (const ch of list) {
    if ("<([".includes(ch)) d++; if (">)]".includes(ch)) d--;
    if (ch === "," && d === 0) { out.push(cur); cur = ""; } else cur += ch;
  }
  if (cur.trim()) out.push(cur);
  return out.map((p) => (p.match(/(\w+)\s*$/) || [])[1]);
};

/** Returns the class-form answer, or null (with a reason) when the answer does not have the simple shape. */
function convert(slug, code) {
  const p = problems[slug];
  const parts = splitTemplate(p.starterCode.cpp, "cpp", { slug, java: p.starterCode.java });
  if (!parts) return [null, "no stub"];
  const stubLines = parts.stub.split("\n");
  const pub = stubLines.findIndex((l) => l.trim() === "public:");
  const methodLine = stubLines[pub + 1];
  const mm = methodLine && methodLine.match(/^\s*(.*?)\b(\w+)\s*\((.*)\)\s*\{\s*$/);
  if (!mm) return [null, "no method line in stub"];
  const [, ret, methodName, lcParams] = mm;
  const lines = code.replace(/\s+$/, "").split("\n");
  const start = lines.findIndex((l) => SOLVE.test(l));
  if (start < 0) return [null, "no solve()"];
  let end = -1;
  for (let i = start + 1; i < lines.length; i++) if (lines[i].trimEnd() === "}") { end = i; break; }
  if (end < 0) return [null, "unterminated solve()"];
  const solveParams = lines[start].match(/\bsolve\((.*)\)\s*\{/)[1];
  if (paramNames(solveParams).join() !== paramNames(lcParams).join()) return [null, "parameter names differ"];
  let body = lines.slice(start + 1, end);
  // A helper with the method's own name (e.g. `rob`) would collide with it: call the helper `<name>Helper`.
  const outside = [...lines.slice(0, start), ...lines.slice(end + 1)];
  const clash = new RegExp(`\\b${methodName}(\\s*\\()`, "g");
  const renameHelper = outside.some((l) => clash.test(l)) && methodName !== "solve";
  clash.lastIndex = 0;
  if (renameHelper) { body = body.map((l) => l.replace(clash, `${methodName}Helper$1`)); outside.forEach((l, i) => { outside[i] = l.replace(clash, `${methodName}Helper$1`); }); }
  body = body.map((l) => l.replace(/\bsolve(\s*\()/g, `${methodName}$1`)); // recursion: the method calls itself
  if (ret.trim() === "void") {
    // The judge's solve() returned the new/mutated board; LeetCode's method edits its argument in place instead.
    const first = paramNames(solveParams)[0];
    let lastIdx = -1;
    for (let i = body.length - 1; i >= 0; i--) if (body[i].trim()) { lastIdx = i; break; }
    body = body.map((l, i) => l.replace(/\breturn\s+([^;]+);/g, (m, expr) => {
      const finalLine = i === lastIdx && /^\s*return\b/.test(l);
      if (expr.trim() === first) return finalLine ? "" : "return;";
      return finalLine ? `${first} = ${expr};` : `{ ${first} = ${expr}; return; }`;
    }));
    while (body.length && !body[body.length - 1].trim()) body.pop();
  }
  const helpers = outside.join("\n").replace(/^\s+|\s+$/g, "");
  const method = `class Solution {\npublic:\n    ${methodLine.trim()}\n${body.map((l) => (l.trim() ? "    " + l : l)).join("\n")}\n    }\n};`;
  return [(helpers ? helpers + "\n\n" : "") + method + "\n", null];
}

let done = 0, kept = 0;
for (const [slug, entry] of Object.entries(solutions)) {
  const code = entry.solutions?.cpp;
  if (!code || /\bclass\s+Solution\b/.test(code) || !problems[slug]) continue;
  const [out, why] = convert(slug, code);
  if (out) { entry.solutions.cpp = out; done++; } else { kept++; console.log(`kept solve-form: ${slug} (${why})`); }
}
fs.writeFileSync(outFile, JSON.stringify(solutions, null, 1) + "\n");
console.log(`converted ${done} C++ answers to class Solution form; ${kept} kept as before -> ${path.relative(ROOT, outFile)}`);
