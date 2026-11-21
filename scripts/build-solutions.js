#!/usr/bin/env node
// Collects the verified reference solutions and editorials under problems/ into the backend's
// classpath resource seed/solutions.json, which the app serves from GET /api/problems/{slug}/solution.
//   node scripts/build-solutions.js
// Re-run it after adding problems or changing a solution/editorial (CI's verify step checks the solutions themselves).
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const dirs = fs.readdirSync(path.join(root, "problems")).sort();
const FILES = { python: "solution.py", java: "solution.java", cpp: "solution.cpp", javascript: "solution.js" };

const out = {};
for (const d of dirs) {
  const dir = path.join(root, "problems", d);
  const metaFile = path.join(dir, "problem.json");
  if (!fs.existsSync(metaFile)) continue;
  const { slug } = JSON.parse(fs.readFileSync(metaFile, "utf8"));
  const solutions = {};
  for (const [lang, file] of Object.entries(FILES)) {
    const p = path.join(dir, file);
    if (fs.existsSync(p)) solutions[lang] = fs.readFileSync(p, "utf8").replace(/\s+$/, "") + "\n";
  }
  if (!Object.keys(solutions).length) continue;
  const edFile = path.join(dir, "editorial.md");
  out[slug] = { editorial: fs.existsSync(edFile) ? fs.readFileSync(edFile, "utf8").trim() : null, solutions };
}

// Answers for the seed problems that are not in problems/ yet (answers/*.txt, verified by scripts/verify-answers.js).
// The explanation comes from the existing study notes (approach and complexity).
const { loadAnswers } = require("./answers-lib");
const study = JSON.parse(fs.readFileSync(path.join(root, "backend/src/main/resources/seed/study.json"), "utf8"));
const ORDER = ["cpp", "java", "python", "javascript"];
for (const [slug, byLang] of Object.entries(loadAnswers())) {
  if (out[slug]) {
    // problems/ holds LeetCode-style `class Solution` files that cannot be pasted into this app's editor (its hidden
    // shell expects `solve`). Show the verified, paste-ready answer instead and keep the problem's own editorial.
    out[slug].solutions = Object.fromEntries(ORDER.filter((l) => byLang[l]).map((l) => [l, byLang[l]]));
    continue;
  }
  const st = study[slug];
  out[slug] = {
    editorial: st ? `## Approach\n\n${st.approach}\n\n**Complexity:** ${st.time} time, ${st.space} space.` : null,
    solutions: Object.fromEntries(ORDER.filter((l) => byLang[l]).map((l) => [l, byLang[l]])),
  };
}

const dest = path.join(root, "backend/src/main/resources/seed/solutions.json");
fs.writeFileSync(dest, JSON.stringify(out, null, 1) + "\n");
console.log(`wrote ${Object.keys(out).length} problems with answers -> ${path.relative(root, dest)}`);
