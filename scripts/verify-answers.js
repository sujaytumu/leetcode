#!/usr/bin/env node
// Runs every answer in answers/*.txt against the problem's real test cases (seed/problems.json), in all languages.
//   node scripts/verify-answers.js [--only slug,slug] [--lang python,cpp] [--file answers/x.txt]
// Output is compared like the judge does: exact after trimming trailing whitespace. Exit code 1 on any failure.
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");
const { ROOT, loadAnswers, splice } = require("./answers-lib");

const arg = (name) => { const i = process.argv.indexOf(name); return i >= 0 ? process.argv[i + 1] : null; };
const only = arg("--only") ? new Set(arg("--only").split(",")) : null;
const langs = (arg("--lang") || "python,javascript,cpp,java").split(",");
const seed = Object.fromEntries(
  JSON.parse(fs.readFileSync(path.join(ROOT, "backend/src/main/resources/seed/problems.json"), "utf8")).map((p) => [p.slug, p]));
const answers = loadAnswers(arg("--file") ? [path.resolve(arg("--file"))] : null);

const hasJavac = spawnSync("javac", ["-version"]).status === 0;
const JAVAC = hasJavac ? ["javac"] : ["java", "-m", "jdk.compiler/com.sun.tools.javac.Main"];
const norm = (s) => s.replace(/\r/g, "").split("\n").map((l) => l.trimEnd()).join("\n").replace(/\s+$/, "");

function sh(cmd, args, opts = {}) {
  return spawnSync(cmd, args, { encoding: "utf8", maxBuffer: 64 << 20, timeout: 120000, ...opts });
}

/** Builds the program for one language; returns the command that runs it (stdin = a test input). */
function build(lang, source, dir) {
  if (lang === "python") { fs.writeFileSync(path.join(dir, "sol.py"), source); return { run: ["python3", ["sol.py"]] }; }
  if (lang === "javascript") { fs.writeFileSync(path.join(dir, "sol.js"), source); return { run: ["node", ["sol.js"]] }; }
  if (lang === "cpp") {
    fs.writeFileSync(path.join(dir, "sol.cpp"), source);
    const c = sh("g++", ["-O2", "-std=c++17", "-o", "sol", "sol.cpp"], { cwd: dir });
    if (c.status !== 0) return { error: "compile error:\n" + c.stderr.slice(0, 600) };
    return { run: ["./sol", []] };
  }
  fs.writeFileSync(path.join(dir, "Main.java"), source);
  const c = sh(JAVAC[0], [...JAVAC.slice(1), "-d", "out", "Main.java"], { cwd: dir });
  if (c.status !== 0) return { error: "compile error:\n" + (c.stderr || c.stdout).slice(0, 600) };
  return { run: ["java", ["-Xss64m", "-cp", "out", "Main"]] };
}

let failures = 0, checked = 0;
for (const [slug, byLang] of Object.entries(answers)) {
  if (only && !only.has(slug)) continue;
  const problem = seed[slug];
  if (!problem) { console.log(`FAIL ${slug}: not in seed/problems.json`); failures++; continue; }
  for (const lang of langs) {
    if (!byLang[lang]) { console.log(`FAIL ${slug} ${lang}: missing answer`); failures++; continue; }
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ans-"));
    let status = "ok";
    try {
      const built = build(lang, splice(problem.starterCode[lang], lang, byLang[lang]), dir);
      if (built.error) status = built.error;
      else {
        for (let i = 0; i < problem.testCases.length; i++) {
          const t = problem.testCases[i];
          const r = sh(built.run[0], built.run[1], { cwd: dir, input: t.input, timeout: 20000 });
          if (r.status !== 0 || r.error) { status = `test ${i + 1}: runtime error ${r.error ? r.error.code : ""}\n${(r.stderr || "").slice(0, 400)}`; break; }
          if (norm(r.stdout) !== norm(t.expectedOutput)) {
            status = `test ${i + 1}: wrong answer\n  input:    ${JSON.stringify(t.input.slice(0, 120))}\n  expected: ${JSON.stringify(norm(t.expectedOutput).slice(0, 120))}\n  got:      ${JSON.stringify(norm(r.stdout).slice(0, 120))}`;
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
console.log(`\n${checked - failures}/${checked} answer checks passed`);
process.exit(failures ? 1 : 0);
