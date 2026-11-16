#!/usr/bin/env node
// Verifies every bundled problem.
//
//   node scripts/verify.js            verify all problems
//   node scripts/verify.js 1 15       verify problems by id
//   node scripts/verify.js --regen    rebuild expected.json from the Python reference
//
// Expected outputs are produced once by the Python reference solution and saved
// in expected.json. The hand-written examples in problem.json are checked
// against the reference independently, and every language must agree with the
// saved expectations. A problem only counts as verified if all of that passes.
const fs = require("fs");
const path = require("path");
const { execute } = require("../runner/execute");
const { LANGS } = require("../runner/lang");

const ROOT = path.join(__dirname, "..", "problems");
const args = process.argv.slice(2);
const regen = args.includes("--regen");
const ids = args.filter((a) => /^\d+$/.test(a)).map(Number);

function loadProblems() {
  return fs
    .readdirSync(ROOT)
    .filter((d) => fs.statSync(path.join(ROOT, d)).isDirectory())
    .sort()
    .map((d) => ({ dir: path.join(ROOT, d), name: d, meta: JSON.parse(fs.readFileSync(path.join(ROOT, d, "problem.json"), "utf8")) }))
    .filter((p) => ids.length === 0 || ids.includes(p.meta.id));
}

async function verifyOne(p) {
  const { meta, dir } = p;
  const problems = [];
  const read = (f) => fs.readFileSync(path.join(dir, f), "utf8");
  const compareMode = meta.compare || "exact";
  const opts = { timeLimitMs: meta.timeLimitMs || 4000, compare: compareMode };

  // 1) examples must match the Python reference.
  const exTests = meta.examples.map((e) => ({ input: e.input, expected: e.output }));
  const ex = await execute("python", read("solution.py"), meta.signature, exTests, opts);
  if (ex.status !== "Accepted") problems.push(`examples vs python: ${ex.status} ${JSON.stringify(ex.failed || ex.message)}`);

  // 2) expected.json from the Python reference.
  const expFile = path.join(dir, "expected.json");
  let expected;
  if (regen || !fs.existsSync(expFile)) {
    const probe = meta.tests.map((input) => ({ input, expected: null }));
    const r = await execute("python", read("solution.py"), meta.signature, probe, { ...opts, stopOnFail: false, compare: "none" });
    const outs = (r.cases || []).map((c) => c.output);
    if (outs.length !== meta.tests.length || (r.cases || []).some((c) => c.status === "Runtime Error" || c.status === "Time Limit Exceeded")) {
      problems.push(`could not generate expected: ${JSON.stringify(r.failed || r.message)}`);
      return problems;
    }
    expected = outs;
    fs.writeFileSync(expFile, JSON.stringify(expected));
  } else expected = JSON.parse(fs.readFileSync(expFile, "utf8"));

  const tests = meta.tests.map((input, i) => ({ input, expected: expected[i] }));

  // 3) every language must pass every test.
  const lines = [];
  for (const lang of Object.keys(LANGS)) {
    const file = `solution.${LANGS[lang].ext}`;
    if (!fs.existsSync(path.join(dir, file))) {
      problems.push(`missing ${file}`);
      continue;
    }
    const r = await execute(lang, read(file), meta.signature, tests, opts);
    lines.push(`${lang}:${r.status === "Accepted" ? r.runtimeMs + "ms" : r.status}`);
    if (r.status !== "Accepted") problems.push(`${lang}: ${r.status} ${JSON.stringify(r.failed || r.message).slice(0, 400)}`);
  }
  if (!fs.existsSync(path.join(dir, "editorial.md"))) problems.push("missing editorial.md");
  return { problems, lines };
}

(async () => {
  const all = loadProblems();
  let bad = 0;
  for (const p of all) {
    const out = await verifyOne(p);
    const problems = Array.isArray(out) ? out : out.problems;
    const detail = Array.isArray(out) ? "" : out.lines.join("  ");
    if (problems.length) {
      bad++;
      console.log(`FAIL  ${p.name}`);
      problems.forEach((x) => console.log("      - " + x));
    } else console.log(`ok    ${p.name}  ${detail}`);
  }
  console.log(`\n${all.length - bad}/${all.length} problems verified`);
  process.exit(bad ? 1 : 0);
})();
