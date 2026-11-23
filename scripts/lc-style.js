// Rewrites the verified `solve`-style reference solutions (the judge's harness form) into LeetCode's own form:
// `class Solution { ... }` with the real method name (C++/Java/Python) or `var name = function` (JavaScript).
// Used by build-solutions.js; the solve-style sources under problems/ and answers/ stay what CI verifies.
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const lcNames = fs.readFileSync(path.join(root, "frontend/lib/lcnames.ts"), "utf8");
const NAMES = Object.fromEntries([...lcNames.split("LC_VOID")[0].matchAll(/"([^"]+)": "(\w+)",/g)].map((m) => [m[1], m[2]]));
const VOID = new Set([...lcNames.split("new Set([")[1].split("])")[0].matchAll(/"([^"]+)"/g)].map((m) => m[1]));
const GRID = Object.fromEntries([...lcNames.split("LC_GRID")[1].matchAll(/"([^"]+)": "(char|int)"/g)].map((m) => [m[1], m[2]]));
const OVERRIDES = JSON.parse(fs.readFileSync(path.join(__dirname, "lc-overrides.json"), "utf8"));
const SNAPSHOT = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(root, "frontend/public/problems-snapshot.json"), "utf8")).map((p) => [p.slug, p]));

const PY = { int: "int", long: "int", boolean: "bool", String: "str", double: "float", ListNode: "Optional[ListNode]", TreeNode: "Optional[TreeNode]" };
const JS = { int: "number", long: "number", boolean: "boolean", String: "string", double: "number", ListNode: "ListNode", TreeNode: "TreeNode" };

function splitParams(s) {
  const out = [];
  let d = 0, cur = "";
  for (const ch of s) {
    if ("<([".includes(ch)) d++;
    if (">)]".includes(ch)) d--;
    if (ch === "," && d === 0) { out.push(cur.trim()); cur = ""; } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
function jsig(slug) {
  const m = /static\s+(.*?)\s+solve\s*\((.*?)\)\s*\{/.exec(SNAPSHOT[slug].starterCode.java);
  const ps = splitParams(m[2]).map((p) => { const i = p.lastIndexOf(" "); return [p.slice(0, i).trim(), p.slice(i + 1).trim()]; });
  return [m[1].trim(), ps];
}
function mt(t, tab, lst) {
  t = t.trim();
  return t.endsWith("[]") ? lst(mt(t.slice(0, -2), tab, lst)) : tab[t] ?? t;
}
const indent = (text, n) => text.split("\n").map((l) => (l.trim() ? " ".repeat(n) + l : l)).join("\n");
function blockEnd(lines, start, closer) {
  for (let i = start + 1; i < lines.length; i++) if (lines[i].trimEnd() === closer) return i;
  return null;
}
function unvoid(body, lang) {
  return lang === "python" ? body.replace(/\breturn\s+\w+\s*$/gm, "return") : body.replace(/\breturn\s+\w+\s*;/g, "return;");
}
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const ptr = (t) => t.replace(/\s*\*\s*/g, "* ").trim();

function conv(slug, lang, code) {
  const name = NAMES[slug];
  const isVoid = VOID.has(slug);
  const [ret, ps] = jsig(slug);
  let lines = code.replace(/\n+$/, "").split("\n");
  if (lang === "python") {
    const si = lines.findIndex((l) => l.startsWith("def solve("));
    if (si < 0) return null;
    let ei = si;
    for (let i = si + 1; i < lines.length; i++) {
      if (lines[i].trim() === "") continue;
      if (/^[ \t]/.test(lines[i])) ei = i; else break;
    }
    let body = lines.slice(si + 1, ei + 1).join("\n");
    body = body.replace(/\bsolve\(/g, `self.${name}(`);
    if (isVoid) body = unvoid(body, "python");
    const helpers = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n").replace(/^\n+|\n+$/g, "");
    const args = ps.map(([t, n]) => `${n}: ${mt(t, PY, (i) => `List[${i}]`)}`).join(", ");
    const r = isVoid ? "None" : mt(ret, PY, (i) => `List[${i}]`);
    return (helpers ? helpers + "\n\n\n" : "") + `class Solution:\n    def ${name}(self, ${args}) -> ${r}:\n` + indent(body, 4) + "\n";
  }
  if (lang === "javascript") {
    const si = lines.findIndex((l) => l.startsWith("function solve("));
    if (si < 0) return null;
    const ei = blockEnd(lines, si, "}");
    if (ei === null) return null;
    let body = lines.slice(si + 1, ei).join("\n");
    let helpers = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n").replace(/^\n+|\n+$/g, "");
    if (name !== "solve" && new RegExp(`function\\s+${name}\\s*\\(`).test(helpers)) {
      helpers = helpers.replace(new RegExp(`\\b${name}\\b`, "g"), name + "Helper");
      body = body.replace(new RegExp(`\\b${name}\\b`, "g"), name + "Helper");
    }
    body = body.replace(/\bsolve\(/g, `${name}(`);
    if (isVoid) body = unvoid(body, "js");
    const doc = ps.map(([t, n]) => ` * @param {${mt(t, JS, (i) => i + "[]")}} ${n}`).join("\n");
    const r = isVoid ? "void" : mt(ret, JS, (i) => i + "[]");
    return (helpers ? helpers + "\n\n" : "") + `/**\n${doc}\n * @return {${r}}\n */\nvar ${name} = function(${ps.map(([, n]) => n).join(", ")}) {\n${body}\n};\n`;
  }
  if (lang === "cpp") {
    const si = lines.findIndex((l) => /^[A-Za-z_].*\bsolve\(.*\)\s*\{\s*$/.test(l));
    if (si < 0) return null;
    const ei = blockEnd(lines, si, "}");
    if (ei === null) return null;
    const m = /^(.*?)\bsolve\((.*)\)\s*\{\s*$/.exec(lines[si]);
    const helpers0 = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n");
    if (name !== "solve" && new RegExp(`^[A-Za-z_][^\\n(]*\\b${name}\\(`, "m").test(helpers0)) {
      lines = lines.map((l, i) => (i !== si ? l.replace(new RegExp(`\\b${name}\\b`, "g"), name + "Helper") : l));
    }
    let body = lines.slice(si + 1, ei).join("\n").replace(/\bsolve\(/g, `${name}(`);
    if (isVoid) body = unvoid(body, "cpp");
    const params = splitParams(m[2]).map((p) => ptr(p.replace(/^(vector<.*>)\s+(\w+)$/, "$1& $2"))).join(", ");
    const r = isVoid ? "void" : ptr(m[1]);
    const helpers = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n").replace(/^\n+|\n+$/g, "");
    return (helpers ? helpers + "\n\n" : "") + `class Solution {\npublic:\n    ${r} ${name}(${params}) {\n` + indent(body, 4) + "\n    }\n};\n";
  }
  if (lang === "java") {
    const si = lines.findIndex((l) => /^static .*\bsolve\(.*\)\s*\{\s*$/.test(l));
    if (si < 0) return null;
    const ei = blockEnd(lines, si, "}");
    if (ei === null) return null;
    const m = /^static\s+(.*?)\s+solve\((.*)\)\s*\{\s*$/.exec(lines[si]);
    const others0 = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n");
    if (name !== "solve" && new RegExp(`\\bstatic\\b[^\\n(]*\\b${name}\\(`).test(others0)) {
      lines = lines.map((l, i) => (i !== si ? l.replace(new RegExp(`\\b${name}\\b`, "g"), name + "Helper") : l));
    }
    let body = lines.slice(si + 1, ei).join("\n").replace(/\bsolve\(/g, `${name}(`);
    if (isVoid) body = unvoid(body, "java");
    const r = isVoid ? "void" : m[1].trim();
    const others = [...lines.slice(0, si), ...lines.slice(ei + 1)].join("\n").replace(/^\n+|\n+$/g, "");
    const parts = [];
    if (others) parts.push(indent(others, 4));
    parts.push(`    public ${r} ${name}(${m[2]}) {\n` + indent(body, 4) + "\n    }");
    return "class Solution {\n" + parts.join("\n\n") + "\n}\n";
  }
  return null;
}

function gridPost(slug, lang, code) {
  const ch = GRID[slug] === "char";
  if (lang === "cpp") {
    code = code.replace(/(?:const\s+)?vector<string>/g, ch ? "vector<vector<char>>" : "vector<vector<int>>");
    if (!ch) {
      code = code.replace(/'(\d)'/g, "$1");
      code = code.replace(/(?:const\s+)?string&\s+row/g, "const vector<int>& row");
      code = code.replace(/(\w) - 0\b/g, "$1");
    }
  } else if (lang === "java") {
    const t = ch ? "char[][]" : "int[][]";
    if (code.includes("String[]")) code = code.split("String[]").join(t);
    code = code.replace(/(\w+(?:\[[^\]]+\])?)\.charAt\(([^()]+)\)/g, (all, a, b) => (a === "word" ? all : `${a}[${b}]`));
    code = code.replace(/(\b(?:grid|board|matrix)\[[^\]]+\])\.length\(\)/g, "$1.length");
    if (!ch) {
      code = code.replace(/'(\d)'/g, "$1");
      code = code.replace("for (String row : grid)", "for (int[] row : grid)");
      code = code.replace(/(\w) - 0\b/g, "$1");
      code = code.replace("char[][] g = new char[rows][];", "int[][] g = grid;");
      code = code.replace(/\n\s*g\[r\] = grid\[r\]\.toCharArray\(\);/, "");
    }
  } else if (lang === "python") {
    code = code.replace(/(grid|board|matrix): List\[str\]/g, `$1: ${ch ? "List[List[str]]" : "List[List[int]]"}`);
    if (!ch) code = code.replace(/(['"])(\d)\1/g, "$2");
  } else if (lang === "javascript") {
    code = code.split("{string[]}").join(ch ? "{character[][]}" : "{number[][]}");
    if (!ch) code = code.replace(/(['"])(\d)\1/g, "$2");
  }
  return code;
}

/** The LeetCode-style source for one reference solution (unchanged when it is already class-style). */
function toLeetCodeStyle(slug, lang, code) {
  if (!NAMES[slug] || !SNAPSHOT[slug]) return code;
  if (OVERRIDES[slug] && OVERRIDES[slug][lang]) return gridPostIf(slug, lang, OVERRIDES[slug][lang]);
  if (/class\s+Solution|var \w+ = function/.test(code)) return gridPostIf(slug, lang, code);
  const out = conv(slug, lang, code);
  return out ? gridPostIf(slug, lang, out) : code;
}
const gridPostIf = (slug, lang, code) => (GRID[slug] ? gridPost(slug, lang, code) : code);

module.exports = { toLeetCodeStyle };
