/**
 * The judge runs a complete program (imports, helper classes, input parsing, printing, and the user's `solve`).
 * The editor should only show the part the user writes, like LeetCode's function stub. This module splits a
 * starter template around its `solve` function and puts the hidden parts back before running or submitting.
 */
import { LC_GRID, LC_METHODS, LC_VOID } from "./lcnames.ts";

export interface Parts { prefix: string; stub: string; suffix: string; lang: string; /** the original `solve` signature line */ sig?: string; /** LeetCode solves this one in place (`void`) */ inPlace?: boolean; /** parameter positions holding string rows that LeetCode types as a char/int grid */ grid?: { kind: "char" | "int"; idx: number[] } }
/** Extra context so the editor can show a LeetCode `class Solution` stub instead of the bare `solve` function. */
export interface StubContext { slug: string; java?: string }

const COMMENT: Record<string, string> = { python: "#", java: "//", cpp: "//", javascript: "//" };
const START: Record<string, RegExp> = {
  python: /^def solve\(/,
  java: /^ {4}static .*\bsolve\(.*\)\s*\{\s*$/,
  cpp: /^[A-Za-z_].*\bsolve\(.*\)\s*\{\s*$/,
  javascript: /^function solve\(/,
};
const OPEN = "<<<LC-USER>>>";
const CLOSE = "<<<LC-END>>>";
const JAVA_INDENT = "    ";

function nodeHint(prefix: string, lang: string): string {
  const c = COMMENT[lang];
  const lines: string[] = [];
  if (/\bListNode\b/.test(prefix)) lines.push(`${c} ListNode is provided: val, next`);
  if (/\bTreeNode\b/.test(prefix)) lines.push(`${c} TreeNode is provided: val, left, right`);
  return lines.length ? lines.join("\n") + "\n" : "";
}

/** Splits a full starter program; null when its shape is not recognised (the caller then shows the whole program). */
export function splitTemplate(template: string, lang: string, ctx?: StubContext): Parts | null {
  const startRe = START[lang];
  if (!startRe) return null;
  const lines = template.split("\n");
  const start = lines.findIndex((l) => startRe.test(l));
  if (start < 0) return null;
  let end = -1;
  if (lang === "python") {
    end = start;
    for (let i = start + 1; i < lines.length; i++) {
      if (lines[i].trim() === "") continue;
      if (/^\s/.test(lines[i])) end = i; else break;
    }
  } else {
    const closer = lang === "java" ? JAVA_INDENT + "}" : "}";
    for (let i = start + 1; i < lines.length; i++) {
      if (lines[i].trimEnd() === closer) { end = i; break; }
    }
  }
  if (end < 0) return null;
  const prefix = lines.slice(0, start).join("\n") + (start > 0 ? "\n" : "");
  const suffix = "\n" + lines.slice(end + 1).join("\n");
  const body = lines.slice(start, end + 1)
    .map((l) => (lang === "java" && l.startsWith(JAVA_INDENT) ? l.slice(JAVA_INDENT.length) : l))
    .join("\n");
  const lc = ctx ? leetCodeStub(body, lang, ctx) : null;
  const gridKind = ctx ? LC_GRID[ctx.slug] : undefined;
  const jsig = ctx ? javaSignature(ctx.java) : null;
  const gridIdx = gridKind && jsig ? jsig.params.flatMap((p, i) => (p.type === "String[]" ? [i] : [])) : [];
  const fullPrefix = lang === "python" && !/from typing import/.test(prefix) ? "from typing import List, Optional\n" + prefix : prefix;
  return { prefix: fullPrefix, stub: nodeHint(prefix, lang) + (lc ?? body), suffix, lang, sig: body.split("\n")[0], inPlace: ctx ? LC_VOID.has(ctx.slug) : false, grid: gridKind && gridIdx.length ? { kind: gridKind, idx: gridIdx } : undefined };
}

const PY_TYPES: Record<string, string> = { int: "int", long: "int", boolean: "bool", String: "str", double: "float", ListNode: "Optional[ListNode]", TreeNode: "Optional[TreeNode]" };
const JS_TYPES: Record<string, string> = { int: "number", long: "number", boolean: "boolean", String: "string", double: "number", ListNode: "ListNode", TreeNode: "TreeNode" };

/** Maps a Java type (`int[][]`, `String[]`, `ListNode`...) to the target language's spelling. */
function mapType(javaType: string, table: Record<string, string>, list: (inner: string) => string): string {
  const t = javaType.trim();
  if (t.endsWith("[]")) return list(mapType(t.slice(0, -2), table, list));
  return table[t] ?? t;
}

function javaSignature(java: string | undefined): { ret: string; params: { type: string; name: string }[] } | null {
  const m = java?.match(/static\s+(.*?)\s+solve\s*\((.*?)\)\s*\{/);
  if (!m) return null;
  const params = splitParams(m[2]).map((p) => {
    const mm = p.trim().match(/^(.*?)\s+(\w+)$/);
    return { type: mm ? mm[1] : "int", name: mm ? mm[2] : p.trim() };
  });
  return { ret: m[1].trim(), params };
}

/** LeetCode's own stub for this problem (class + real method name), built from the `solve` signature; null when unknown. */
function leetCodeStub(body: string, lang: string, ctx: StubContext): string | null {
  const name = LC_METHODS[ctx.slug];
  if (!name) return null;
  const isVoid = LC_VOID.has(ctx.slug);
  const first = body.split("\n")[0];
  if (lang === "cpp") {
    const m = first.match(/^(.*?)\bsolve\((.*)\)\s*\{\s*$/);
    if (!m) return null;
    const ptr = (t: string) => t.replace(/\s*\*\s*/g, "* ").trim();
    const gk = LC_GRID[ctx.slug];
    const gridT = gk === "char" ? "vector<vector<char>>" : "vector<vector<int>>";
    const params = splitParams(m[2]).map((p) => ptr((gk ? p.replace(/^vector<string>\s+(\w+)$/, `${gridT} $1`) : p).replace(/^(vector<.*>)\s+(\w+)$/, "$1& $2"))).join(", ");
    return `class Solution {\npublic:\n    ${isVoid ? "void" : ptr(m[1])} ${name}(${params}) {\n        \n    }\n};`;
  }
  if (lang === "java") {
    const m = first.match(/^static\s+(.*?)\s+solve\((.*)\)\s*\{\s*$/);
    if (!m) return null;
    const gk = LC_GRID[ctx.slug];
    const jparams = gk ? m[2].replace(/String\[\]\s+(\w+)/g, `${gk === "char" ? "char" : "int"}[][] $1`) : m[2];
    return `class Solution {\n    public ${isVoid ? "void" : m[1].trim()} ${name}(${jparams}) {\n        \n    }\n}`;
  }
  const sig = javaSignature(ctx.java);
  if (!sig) return null;
  if (lang === "python") {
    const gk = LC_GRID[ctx.slug];
    const ps = sig.params.map((p) => `${p.name}: ${gk && p.type === "String[]" ? (gk === "char" ? "List[List[str]]" : "List[List[int]]") : mapType(p.type, PY_TYPES, (i) => `List[${i}]`)}`).join(", ");
    const ret = isVoid ? "None" : mapType(sig.ret, PY_TYPES, (i) => `List[${i}]`);
    return `class Solution:\n    def ${name}(self${ps ? ", " + ps : ""}) -> ${ret}:\n        `;
  }
  if (lang === "javascript") {
    const gk = LC_GRID[ctx.slug];
    const doc = sig.params.map((p) => ` * @param {${gk && p.type === "String[]" ? (gk === "char" ? "character[][]" : "number[][]") : mapType(p.type, JS_TYPES, (i) => `${i}[]`)}} ${p.name}`).join("\n");
    const ret = isVoid ? "void} Do not return anything, modify the input in-place instead." : `${mapType(sig.ret, JS_TYPES, (i) => `${i}[]`)}}`;
    return `/**\n${doc}\n * @return {${ret}\n */\nvar ${name} = function(${sig.params.map((p) => p.name).join(", ")}) {\n    \n};`;
  }
  return null;
}

const NOT_METHODS = new Set(["if", "for", "while", "switch", "return", "catch", "Solution", "sizeof"]);

/** Splits a parameter list on its top-level commas (generics like `map<int, int>` stay whole). */
function splitParams(params: string): string[] {
  const out: string[] = [];
  let depth = 0;
  let cur = "";
  for (const ch of params) {
    if ("<([".includes(ch)) depth++;
    if (">)]".includes(ch)) depth--;
    if (ch === "," && depth === 0) { out.push(cur.trim()); cur = ""; } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

/**
 * LeetCode-style code (`class Solution { ... twoSum(...) }`) has no `solve`, which the hidden program calls.
 * Returns a small forwarding `solve` built from the stub's own signature, or "" when the code already defines `solve`.
 * In-place (`void`) methods answer with their first argument, like LeetCode checks the mutated input.
 */
function leetCodeAdapter(parts: Parts, user: string): string {
  const lang = parts.lang;
  if (/^[^\s}].*\bsolve\s*\(/m.test(user)) return "";
  if (lang === "javascript") {
    const ret = parts.inPlace ? "args[0]" : "r";
    const conv = parts.grid ? parts.grid.idx.map((i) => `args[${i}] = args[${i}].map((row) => ${parts.grid!.kind === "char" ? 'row.split("")' : 'row.split("").map(Number)'});`).join(" ") : "";
    const vars = [...user.matchAll(/^(?:var|let|const)\s+(\w+)\s*=\s*function\b/gm)].map((x) => x[1]);
    if (vars.includes("solve")) {
      // LeetCode's own name for this problem is `solve`; wrap it so in-place answers are returned.
      return `\nsolve = ((__lc) => (...args) => { ${conv} const r = __lc(...args); return ${ret}; })(solve);\n`;
    }
    const m = vars.length ? vars[vars.length - 1] : [...user.matchAll(/function\s+(\w+)\s*\(/g)].map((x) => x[1]).find((n) => n !== "solve");
    return m ? `\nfunction solve(...args) { ${conv} const r = ${m}(...args); return ${ret}; }\n` : "";
  }
  if (!/\bclass\s+Solution\b/.test(user)) return "";
  const afterClass = user.slice(user.search(/\bclass\s+Solution\b/));
  if (lang === "python") {
    const method = [...afterClass.matchAll(/def\s+(\w+)\s*\(\s*self/g)].map((x) => x[1]).find((n) => !n.startsWith("__"));
    const pconv = parts.grid ? `    args = list(args)\n` + parts.grid.idx.map((i) => `    args[${i}] = [${parts.grid!.kind === "char" ? "list(row)" : "[int(c) for c in row]"} for row in args[${i}]]\n`).join("") : "";
    return method ? `\ndef solve(*args):\n${pconv}    r = Solution().${method}(*args)\n    return ${parts.inPlace ? "args[0]" : "r"}\n` : "";
  }
  if (lang !== "cpp" && lang !== "java") return "";
  const sig = parts.sig ?? parts.stub.split("\n").find((l) => /\bsolve\s*\(/.test(l));
  const m = sig?.match(/^(.*?)\bsolve\s*\((.*)\)\s*\{?\s*:?\s*$/);
  if (!m) return "";
  const head = m[1];
  const rawParams = m[2];
  // LeetCode's entry point is the first public method; helpers (private/static) may be declared above it.
  const publicMethod = lang === "java"
    ? [...afterClass.matchAll(/\bpublic\s+(?:static\s+)?[\w<>\[\],.?\s]+?\s+(\w+)\s*\(/g)].map((x) => x[1]).find((n) => !NOT_METHODS.has(n))
    : undefined;
  const method = publicMethod ?? [...afterClass.matchAll(/(\w+)\s*\([^;{)]*\)\s*(?:const\s*)?\{/g)].map((x) => x[1]).find((n) => !NOT_METHODS.has(n));
  if (!method) return "";
  const names = splitParams(rawParams).map((p) => p.match(/(\w+)\s*(?:\[\s*\])*\s*$/)?.[1] ?? "").filter(Boolean);
  const userVoid = new RegExp(`\\bvoid\\s+${method}\\s*\\(`).test(afterClass);
  const ctor = lang === "java" ? "new Solution()" : "Solution()";
  const argExprs = names.slice();
  let pre = "";
  for (const i of parts.grid?.idx ?? []) {
    const n = names[i];
    const kind = parts.grid!.kind;
    if (lang === "cpp") {
      pre += kind === "char"
        ? `vector<vector<char>> ${n}_g; for (auto &row : ${n}) ${n}_g.emplace_back(row.begin(), row.end()); `
        : `vector<vector<int>> ${n}_g; for (auto &row : ${n}) { vector<int> r2; for (char ch : row) r2.push_back(ch - '0'); ${n}_g.push_back(r2); } `;
    } else {
      pre += kind === "char"
        ? `char[][] ${n}_g = new char[${n}.length][]; for (int i = 0; i < ${n}.length; i++) ${n}_g[i] = ${n}[i].toCharArray(); `
        : `int[][] ${n}_g = new int[${n}.length][]; for (int i = 0; i < ${n}.length; i++) { ${n}_g[i] = new int[${n}[i].length()]; for (int j = 0; j < ${n}[i].length(); j++) ${n}_g[i][j] = ${n}[i].charAt(j) - '0'; } `;
    }
    argExprs[i] = `${n}_g`;
  }
  const call = `${ctor}.${method}(${argExprs.join(", ")})`;
  const stubVoid = /\bvoid\s*$/.test(head.trim());
  const bodyText = pre + (userVoid && !stubVoid ? `${call}; return ${names[0]};` : stubVoid ? `${call};` : `return ${call};`);
  const fn = `${head}solve(${rawParams}) { ${bodyText} }`;
  return lang === "java" ? `\n${JAVA_INDENT}${fn}\n` : `\n${fn}\n`;
}

/** The full program to send to the judge: the hidden parts around the user's code. */
/** The marker the judge splits on: user prints come before it, the answer after it (see SubmissionService.ANSWER_MARKER). */
const MARK: Record<string, string> = {
  cpp: "cout << '\\x1e';",
  java: "System.out.print((char) 30);",
  python: "print('\\x1e', end='')",
  javascript: "process.stdout.write('\\x1e');",
};

/**
 * Prints the answer marker right after the hidden main calls `solve`, so anything the user's code prints (cout, print,
 * console.log, System.out) lands before it and shows in a separate "Stdout" box instead of breaking the answer.
 * C++ also stops un-syncing cout from stdio, so printf and cout keep their order.
 */
export function markAnswer(suffix: string, lang: string): string {
  const mark = MARK[lang];
  if (!mark) return suffix;
  let out = lang === "cpp" ? suffix.replace(/^\s*ios::sync_with_stdio\(false\);\s*\n/m, "") : suffix;
  out = out.replace(/^(\s*)(.*\bresult\s*=\s*solve\(.*\);?)[ \t]*$/m, (_m, indent: string, call: string) => `${indent}${call}\n${indent}${mark}`);
  return out;
}

export function composeProgram(parts: Parts, user: string): string {
  const c = COMMENT[parts.lang];
  let body = user.replace(/\s+$/, "");
  if (parts.lang === "java") body = body.replace(/^(\s*)((?:public\s+)?)class\s+Solution\b/m, "$1static class Solution");
  const adapter = leetCodeAdapter(parts, user);
  const placed = parts.lang === "java"
    ? body.split("\n").map((l) => (l.trim() ? JAVA_INDENT + l : l)).join("\n")
    : body;
  return `${parts.prefix}${c} ${OPEN}\n${placed}\n${c} ${CLOSE}${adapter}${markAnswer(parts.suffix, parts.lang)}`;
}

/** The user's part of a program built by composeProgram (e.g. an earlier submission); null when it has no markers. */
export function extractUser(full: string, lang: string): string | null {
  const m = full.match(new RegExp(`^.*${OPEN}.*\\n([\\s\\S]*?)\\n.*${CLOSE}.*$`, "m"));
  if (!m) return null;
  return lang === "java"
    ? m[1].split("\n").map((l) => (l.startsWith(JAVA_INDENT) ? l.slice(JAVA_INDENT.length) : l)).join("\n")
    : m[1];
}

/** Compiler and runtime messages point into the full program; show line numbers relative to the user's code instead. */
export function shiftErrorLines(text: string, parts: Parts): string {
  const offset = parts.prefix.split("\n").length; // prefix lines + the opening marker line
  const shift = (n: number) => (n > offset ? n - offset : n);
  return text
    .replace(/(\.(?:java|cpp|cc|py|js)):(\d+)/g, (_m, ext: string, n: string) => `${ext}:${shift(Number(n))}`)
    .replace(/\bline (\d+)\b/g, (_m, n: string) => `line ${shift(Number(n))}`);
}
