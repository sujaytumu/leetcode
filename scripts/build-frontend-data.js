#!/usr/bin/env node
// Writes the problem catalog and problem text into frontend/public/data so the site can render the
// problem list and every problem page instantly, even while the free-tier backend is asleep.
// The backend is still needed for progress, bookmarks and running code.
//
//   node scripts/build-frontend-data.js          regenerate
//   node scripts/build-frontend-data.js --check  exit 1 if the committed files are out of date
const fs = require("fs");
const path = require("path");

const seedFile = path.join(__dirname, "..", "backend", "src", "main", "resources", "seed", "problems.json");
const outDir = path.join(__dirname, "..", "frontend", "public", "data");
const check = process.argv.includes("--check");

const seed = JSON.parse(fs.readFileSync(seedFile, "utf8"));
const files = new Map();

// ids follow seed order, which is the order the backend inserts rows in.
files.set(
  "catalog.json",
  JSON.stringify(seed.map((p, i) => ({ id: i + 1, slug: p.slug, title: p.title, difficulty: p.difficulty, tags: p.tags }))),
);
for (const p of seed) {
  files.set(
    `problems/${p.slug}.json`,
    JSON.stringify({
      description: p.description,
      starterCode: p.starterCode,
      samples: p.testCases.filter((t) => t.sample).map((t) => ({ input: t.input, expectedOutput: t.expectedOutput })),
    }),
  );
}

if (check) {
  const stale = [];
  for (const [name, content] of files) {
    const f = path.join(outDir, name);
    if (!fs.existsSync(f) || fs.readFileSync(f, "utf8") !== content) stale.push(name);
  }
  const existing = fs.existsSync(path.join(outDir, "problems")) ? fs.readdirSync(path.join(outDir, "problems")) : [];
  for (const f of existing) if (!files.has(`problems/${f}`)) stale.push(`problems/${f} (no longer in the seed)`);
  if (stale.length) {
    console.error(`frontend/public/data is out of date (${stale.length} files). Run: node scripts/build-frontend-data.js`);
    console.error(stale.slice(0, 5).join("\n"));
    process.exit(1);
  }
  console.log(`frontend data is up to date (${seed.length} problems)`);
} else {
  fs.mkdirSync(path.join(outDir, "problems"), { recursive: true });
  for (const f of fs.readdirSync(path.join(outDir, "problems"))) {
    if (!files.has(`problems/${f}`)) fs.rmSync(path.join(outDir, "problems", f));
  }
  for (const [name, content] of files) fs.writeFileSync(path.join(outDir, name), content);
  console.log(`wrote catalog + ${seed.length} problem files to frontend/public/data`);
}
