#!/usr/bin/env node
// End-to-end "paste test": takes the code the Solutions tab shows, runs it through the editor's own
// splitTemplate/composeProgram (frontend/lib/harness.ts), compiles it and runs every test case, like Submit does.
//   node scripts/verify-paste.mjs [--lang cpp,python,java,javascript] [--only slug,slug] [--from solutions.json]
// Exit code 1 on any failure.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { splitTemplate, composeProgram } from "../frontend/lib/harness.ts";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const arg = (n) => { const i = process.argv.indexOf(n); return i >= 0 ? process.argv[i + 1] : null; };
const langs = (arg("--lang") || "cpp").split(",");
const only = arg("--only") ? new Set(arg("--only").split(",")) : null;
const solFile = arg("--from") || path.join(ROOT, "backend/src/main/resources/seed/solutions.json");
const solutions = JSON.parse(fs.readFileSync(solFile, "utf8"));
const problems = Object.fromEntries(
  JSON.parse(fs.readFileSync(path.join(ROOT, "backend/src/main/resources/seed/problems.json"), "utf8")).map((p) => [p.slug, p]));

const hasJavac = spawnSync("javac", ["-version"]).status === 0;
const JAVAC = hasJavac ? ["javac"] : ["java", "-m", "jdk.compiler/com.sun.tools.javac.Main"];
const norm = (s) => s.replace(/\r/g, "").split("\n").map((l) => l.trimEnd()).join("\n").replace(/\s+$/, "");
const sh = (cmd, args, opts = {}) => spawnSync(cmd, args, { encoding: "utf8", maxBuffer: 64 << 20, timeout: 120000, ...opts });

function build(lang, source, dir) {
  if (lang === "python") { fs.writeFileSync(path.join(dir, "sol.py"), source); return { run: ["python3", ["sol.py"]] }; }
  if (lang === "javascript") { fs.writeFileSync(path.join(dir, "sol.js"), source); return { run: ["node", ["sol.js"]] }; }
  if (lang === "cpp") {
    fs.writeFileSync(path.join(dir, "sol.cpp"), source);
    const c = sh("g++", ["-O2", "-std=c++17", "-o", "sol", "sol.cpp"], { cwd: dir });
    return c.status === 0 ? { run: ["./sol", []] } : { error: "compile error:\n" + c.stderr.slice(0, 500) };
  }
  fs.writeFileSync(path.join(dir, "Main.java"), source);
  const c = sh(JAVAC[0], [...JAVAC.slice(1), "-d", "out", "Main.java"], { cwd: dir });
  return c.status === 0 ? { run: ["java", ["-Xss64m", "-cp", "out", "Main"]] } : { error: "compile error:\n" + (c.stderr || c.stdout).slice(0, 500) };
}

let failures = 0, checked = 0;
for (const [slug, entry] of Object.entries(solutions)) {
  if (only && !only.has(slug)) continue;
  const problem = problems[slug];
  if (!problem) continue;
  for (const lang of langs) {
    const code = entry.solutions?.[lang];
    if (!code) { failures++; checked++; console.log(`FAIL ${slug} ${lang}: no solution shown`); continue; }
    const starter = problem.starterCode[lang];
    const parts = splitTemplate(starter, lang, { slug, java: problem.starterCode.java });
    if (!parts) { failures++; checked++; console.log(`FAIL ${slug} ${lang}: template not recognised`); continue; }
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "paste-"));
    let status = "ok";
    try {
      const built = build(lang, composeProgram(parts, code), dir);
      if (built.error) status = built.error;
      else {
        for (let i = 0; i < problem.testCases.length; i++) {
          const t = problem.testCases[i];
          const r = sh(built.run[0], built.run[1], { cwd: dir, input: t.input, timeout: 20000 });
          if (r.status !== 0 || r.error) { status = `test ${i + 1}: runtime error ${r.error ? r.error.code : ""}\n${(r.stderr || "").slice(0, 300)}`; break; }
          if (norm(r.stdout) !== norm(t.expectedOutput)) {
            status = `test ${i + 1}: wrong answer\n  expected: ${JSON.stringify(norm(t.expectedOutput).slice(0, 100))}\n  got:      ${JSON.stringify(norm(r.stdout).slice(0, 100))}`;
            break;
          }
        }
      }
    } catch (e) { status = String(e.message || e); }
    fs.rmSync(dir, { recursive: true, force: true });
    checked++;
    if (status === "ok") console.log(`ok   ${slug} ${lang} (${problem.testCases.length} tests)`);
    else { failures++; console.log(`FAIL ${slug} ${lang}: ${status}`); }
  }
}
console.log(`\n${checked - failures}/${checked} paste checks passed`);
process.exit(failures ? 1 : 0);
