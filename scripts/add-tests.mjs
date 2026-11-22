#!/usr/bin/env node
// Adds hidden test cases to problems.json from tests-extra/*.json ({slug: ["stdin", ...]}).
// Expected output = the Solutions-tab C++ run through the editor path; a new case is kept only if the
// brute-force C++ (when present) and the Python/Java/JS solutions (when present) print exactly the same.
//   node scripts/add-tests.mjs [--dry] [--only slug,slug]
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { splitTemplate, composeProgram } from "../frontend/lib/harness.ts";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n) => { const i = process.argv.indexOf(n); return i >= 0 ? process.argv[i + 1] : null; };
const dry = process.argv.includes("--dry");
const only = arg("--only") ? new Set(arg("--only").split(",")) : null;
const PF = path.join(ROOT, "backend/src/main/resources/seed/problems.json");
const problemsArr = JSON.parse(fs.readFileSync(PF, "utf8"));
const sols = JSON.parse(fs.readFileSync(path.join(ROOT, "backend/src/main/resources/seed/solutions.json"), "utf8"));
const norm = (s) => s.replace(/\r/g, "").split("\n").map((l) => l.trimEnd()).join("\n").replace(/\s+$/, "");
const sh = (c, a, o = {}) => spawnSync(c, a, { encoding: "utf8", maxBuffer: 64 << 20, timeout: 60000, ...o });

function build(problem, lang, code) {
  const parts = splitTemplate(problem.starterCode[lang], lang, { slug: problem.slug, java: problem.starterCode.java });
  if (!parts) return null;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "addt-"));
  const src = composeProgram(parts, code);
  if (lang === "cpp") {
    fs.writeFileSync(path.join(dir, "s.cpp"), src);
    if (sh("g++", ["-O2", "-std=c++17", "-o", "s", "s.cpp"], { cwd: dir }).status) return null;
    return { dir, cmd: ["./s", []] };
  }
  if (lang === "python") { fs.writeFileSync(path.join(dir, "s.py"), src); return { dir, cmd: ["python3", ["s.py"]] }; }
  if (lang === "javascript") { fs.writeFileSync(path.join(dir, "s.js"), src); return { dir, cmd: ["node", ["s.js"]] }; }
  return null; // java skipped: slow to compile per problem; cpp+brute+python is enough
}
const run = (b, input) => { const r = sh(b.cmd[0], b.cmd[1], { cwd: b.dir, input, timeout: 10000 }); return r.status === 0 && !r.error ? norm(r.stdout) : null; };

const extra = {};
for (const f of fs.readdirSync(path.join(ROOT, "tests-extra")).filter((f) => f.endsWith(".json")))
  Object.assign(extra, JSON.parse(fs.readFileSync(path.join(ROOT, "tests-extra", f), "utf8")));

let added = 0, dropped = 0;
for (const p of problemsArr) {
  const inputs = extra[p.slug];
  if (!inputs || (only && !only.has(p.slug))) continue;
  const e = sols[p.slug] || {};
  const main = build(p, "cpp", e.solutions?.cpp || "");
  if (!main) { console.log(`SKIP ${p.slug}: cannot build main`); continue; }
  const checks = [];
  if (e.bruteForce?.cpp) { const b = build(p, "cpp", e.bruteForce.cpp); if (b) checks.push(b); }
  for (const l of ["python", "javascript"]) if (e.solutions?.[l]) { const b = build(p, l, e.solutions[l]); if (b) checks.push(b); }
  const have = new Set(p.testCases.map((t) => norm(t.input)));
  let ok = 0;
  for (const raw of inputs) {
    const input = raw.endsWith("\n") ? raw : raw + "\n";
    if (have.has(norm(input))) continue;
    const out = run(main, input);
    if (out === null || out === "") { dropped++; console.log(`drop ${p.slug}: main failed`); continue; }
    if (checks.some((c) => run(c, input) !== out)) { dropped++; console.log(`drop ${p.slug}: solutions disagree`); continue; }
    p.testCases.push({ input, expectedOutput: out + "\n", sample: false });
    have.add(norm(input)); ok++; added++;
  }
  for (const b of [main, ...checks]) fs.rmSync(b.dir, { recursive: true, force: true });
  console.log(`${p.slug}: +${ok}`);
}
if (!dry) fs.writeFileSync(PF, JSON.stringify(problemsArr, null, 2) + "\n");
console.log(`\nadded ${added}, dropped ${dropped}${dry ? " (dry run)" : ""}`);
