#!/usr/bin/env node
// Writes problems-src/*.js specs into problems/<id>-<slug>/ folders.
//   node scripts/materialize.js problems-src/batch1.js [more files...]
// Existing expected.json files are removed so verify regenerates them.
const fs = require("fs");
const path = require("path");

const files = process.argv.slice(2);
if (!files.length) {
  console.error("usage: materialize.js <spec.js>...");
  process.exit(1);
}

let n = 0;
for (const f of files) {
  for (const p of require(path.resolve(f))) {
    const dir = path.join(__dirname, "..", "problems", `${String(p.id).padStart(4, "0")}-${p.slug}`);
    fs.mkdirSync(dir, { recursive: true });
    const { py, cpp, java, editorial, ...meta } = p;
    meta.compare = meta.compare || "exact";
    meta.timeLimitMs = meta.timeLimitMs || 3000;
    fs.writeFileSync(path.join(dir, "problem.json"), JSON.stringify(meta, null, 2) + "\n");
    fs.writeFileSync(path.join(dir, "solution.py"), py);
    fs.writeFileSync(path.join(dir, "solution.cpp"), cpp);
    fs.writeFileSync(path.join(dir, "solution.java"), java);
    fs.writeFileSync(path.join(dir, "editorial.md"), editorial + "\n");
    fs.rmSync(path.join(dir, "expected.json"), { force: true });
    n++;
  }
}
console.log(`materialized ${n} problems`);
