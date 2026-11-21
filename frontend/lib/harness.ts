/**
 * The judge runs a complete program (imports, helper classes, input parsing, printing, and the user's `solve`).
 * The editor should only show the part the user writes, like LeetCode's function stub. This module splits a
 * starter template around its `solve` function and puts the hidden parts back before running or submitting.
 */
export interface Parts { prefix: string; stub: string; suffix: string; lang: string }

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
export function splitTemplate(template: string, lang: string): Parts | null {
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
  return { prefix, stub: nodeHint(prefix, lang) + body, suffix, lang };
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
 * Returns a small forwarding `solve` built from the stub's own signature, or "" when the code already defines `solve`
 * or is not shaped like a Solution class.
 */
function leetCodeAdapter(parts: Parts, user: string): string {
  const lang = parts.lang;
  if (!/\bclass\s+Solution\b/.test(user) || /\bsolve\s*\(/.test(user)) return "";
  const sig = parts.stub.split("\n").find((l) => /\bsolve\s*\(/.test(l));
  if (!sig) return "";
  const m = sig.match(/^(.*?)\bsolve\s*\((.*)\)\s*\{?\s*:?\s*$/);
  if (!m) return "";
  const head = m[1];
  const rawParams = m[2];
  const afterClass = user.slice(user.search(/\bclass\s+Solution\b/));
  let method: string | undefined;
  if (lang === "python") {
    method = [...afterClass.matchAll(/def\s+(\w+)\s*\(\s*self/g)].map((x) => x[1]).find((n) => !n.startsWith("__"));
    if (!method) return "";
    return `\ndef solve(*args):\n    return Solution().${method}(*args)\n`;
  }
  if (lang !== "cpp" && lang !== "java") return "";
  method = [...afterClass.matchAll(/(\w+)\s*\([^;{)]*\)\s*(?:const\s*)?\{/g)].map((x) => x[1]).find((n) => !NOT_METHODS.has(n));
  if (!method) return "";
  const names = splitParams(rawParams).map((p) => p.match(/(\w+)\s*(?:\[\s*\])*\s*$/)?.[1] ?? "").filter(Boolean);
  const isVoid = /\bvoid\s*$/.test(head.trim());
  const ctor = lang === "java" ? "new Solution()" : "Solution()";
  const call = `${ctor}.${method}(${names.join(", ")})`;
  const fn = `${head}solve(${rawParams}) { ${isVoid ? "" : "return "}${call}; }`;
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
