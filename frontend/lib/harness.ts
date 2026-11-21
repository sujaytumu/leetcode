/**
 * The judge runs a complete program (imports, helper classes, input parsing, printing, and the user's `solve`).
 * The editor should only show the part the user writes, like LeetCode's function stub. This module splits a
 * starter template around its `solve` function and puts the hidden parts back before running or submitting.
 */
import { LC_METHODS, LC_VOID } from "./lcnames.ts";

export interface Parts { prefix: string; stub: string; suffix: string; lang: string; /** the original `solve` signature line */ sig?: string }
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
  const fullPrefix = lang === "python" && !/from typing import/.test(prefix) ? "from typing import List, Optional\n" + prefix : prefix;
  return { prefix: fullPrefix, stub: nodeHint(prefix, lang) + (lc ?? body), suffix, lang, sig: body.split("\n")[0] };
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
    const params = splitParams(m[2]).map((p) => ptr(p.replace(/^(vector<.*>)\s+(\w+)$/, "$1& $2"))).join(", ");
    return `class Solution {\npublic:\n    ${isVoid ? "void" : ptr(m[1])} ${name}(${params}) {\n        \n    }\n};`;
  }
  if (lang === "java") {
    const m = first.match(/^static\s+(.*?)\s+solve\((.*)\)\s*\{\s*$/);
    if (!m) return null;
    return `class Solution {\n    public ${isVoid ? "void" : m[1].trim()} ${name}(${m[2]}) {\n        \n    }\n}`;
  }
  const sig = javaSignature(ctx.java);
  if (!sig) return null;
  if (lang === "python") {
    const ps = sig.params.map((p) => `${p.name}: ${mapType(p.type, PY_TYPES, (i) => `List[${i}]`)}`).join(", ");
    const ret = isVoid ? "None" : mapType(sig.ret, PY_TYPES, (i) => `List[${i}]`);
    return `class Solution:\n    def ${name}(self${ps ? ", " + ps : ""}) -> ${ret}:\n        `;
  }
  if (lang === "javascript") {
    const doc = sig.params.map((p) => ` * @param {${mapType(p.type, JS_TYPES, (i) => `${i}[]`)}} ${p.name}`).join("\n");
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
    const m = [...user.matchAll(/(?:var|let|const)\s+(\w+)\s*=\s*(?:function|\()|function\s+(\w+)\s*\(/g)].map((x) => x[1] ?? x[2]).find((n) => n && n !== "solve");
    return m ? `\nfunction solve(...args) { const r = ${m}(...args); return r === undefined ? args[0] : r; }\n` : "";
  }
  if (!/\bclass\s+Solution\b/.test(user)) return "";
  const afterClass = user.slice(user.search(/\bclass\s+Solution\b/));
  if (lang === "python") {
    const method = [...afterClass.matchAll(/def\s+(\w+)\s*\(\s*self/g)].map((x) => x[1]).find((n) => !n.startsWith("__"));
    return method ? `\ndef solve(*args):\n    r = Solution().${method}(*args)\n    return args[0] if r is None else r\n` : "";
  }
  if (lang !== "cpp" && lang !== "java") return "";
  const sig = parts.sig ?? parts.stub.split("\n").find((l) => /\bsolve\s*\(/.test(l));
  const m = sig?.match(/^(.*?)\bsolve\s*\((.*)\)\s*\{?\s*:?\s*$/);
  if (!m) return "";
  const head = m[1];
  const rawParams = m[2];
  const method = [...afterClass.matchAll(/(\w+)\s*\([^;{)]*\)\s*(?:const\s*)?\{/g)].map((x) => x[1]).find((n) => !NOT_METHODS.has(n));
  if (!method) return "";
  const names = splitParams(rawParams).map((p) => p.match(/(\w+)\s*(?:\[\s*\])*\s*$/)?.[1] ?? "").filter(Boolean);
  const userVoid = new RegExp(`\\bvoid\\s+${method}\\s*\\(`).test(afterClass);
  const ctor = lang === "java" ? "new Solution()" : "Solution()";
  const call = `${ctor}.${method}(${names.join(", ")})`;
  const stubVoid = /\bvoid\s*$/.test(head.trim());
  const bodyText = userVoid && !stubVoid ? `${call}; return ${names[0]};` : stubVoid ? `${call};` : `return ${call};`;
  const fn = `${head}solve(${rawParams}) { ${bodyText} }`;
  return lang === "java" ? `\n${JAVA_INDENT}${fn}\n` : `\n${fn}\n`;
}

/** The full program to send to the judge: the hidden parts around the user's code. */
export function composeProgram(parts: Parts, user: string): string {
  const c = COMMENT[parts.lang];
  let body = user.replace(/\s+$/, "");
  if (parts.lang === "java") body = body.replace(/^(\s*)((?:public\s+)?)class\s+Solution\b/m, "$1static class Solution");
  const adapter = leetCodeAdapter(parts, user);
  const placed = parts.lang === "java"
    ? body.split("\n").map((l) => (l.trim() ? JAVA_INDENT + l : l)).join("\n")
    : body;
  return `${parts.prefix}${c} ${OPEN}\n${placed}\n${c} ${CLOSE}${adapter}${parts.suffix}`;
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
