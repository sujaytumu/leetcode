// Shared helpers for the answers/*.txt files (reference answers for the seed problems).
//
// File format (one or many problems per file):
//   === problem-slug
//   --- py
//   def solve(...): ...
//   --- js
//   --- cpp
//   --- java
// Each section holds exactly the code a user would write in the editor: the `solve` function plus any helpers.
// The hidden shell (imports, input parsing, printing) comes from the problem's starter template.
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const KEYS = { py: "python", js: "javascript", cpp: "cpp", java: "java" };
const START = {
  python: /^def solve\(/,
  java: /^ {4}static .*\bsolve\(.*\)\s*\{\s*$/,
  cpp: /^[A-Za-z_].*\bsolve\(.*\)\s*\{\s*$/,
  javascript: /^function solve\(/,
};

function loadAnswers(files) {
  const dir = path.join(ROOT, "answers");
  const names = files || fs.readdirSync(dir).filter((f) => f.endsWith(".txt")).sort().map((f) => path.join(dir, f));
  const out = {};
  for (const file of names) {
    let slug = null, lang = null, buf = [];
    const flush = () => {
      if (slug && lang) out[slug][lang] = buf.join("\n").replace(/\s+$/, "") + "\n";
      buf = [];
    };
    for (const line of fs.readFileSync(file, "utf8").split("\n")) {
      let m;
      if ((m = line.match(/^=== (\S+)\s*$/))) { flush(); slug = m[1]; lang = null; out[slug] = out[slug] || {}; }
      else if ((m = line.match(/^--- (py|js|cpp|java)\s*$/))) { flush(); lang = KEYS[m[1]]; }
      else if (lang) buf.push(line);
    }
    flush();
  }
  return out;
}

/** Puts the answer in place of the `solve` function of a full starter template. */
function splice(template, lang, answer) {
  const lines = template.split("\n");
  const start = lines.findIndex((l) => START[lang].test(l));
  if (start < 0) throw new Error(`no solve() in ${lang} template`);
  let end = -1;
  if (lang === "python") {
    end = start;
    for (let i = start + 1; i < lines.length; i++) {
      if (lines[i].trim() === "") continue;
      if (/^\s/.test(lines[i])) end = i; else break;
    }
  } else {
    const closer = lang === "java" ? "    }" : "}";
    for (let i = start + 1; i < lines.length; i++) if (lines[i].trimEnd() === closer) { end = i; break; }
  }
  if (end < 0) throw new Error(`unterminated solve() in ${lang} template`);
  const prefix = lines.slice(0, start).join("\n") + (start > 0 ? "\n" : "");
  const suffix = "\n" + lines.slice(end + 1).join("\n");
  const body = answer.replace(/\s+$/, "");
  const placed = lang === "java" ? body.split("\n").map((l) => (l.trim() ? "    " + l : l)).join("\n") : body;
  return prefix + placed + suffix;
}

module.exports = { ROOT, loadAnswers, splice };
