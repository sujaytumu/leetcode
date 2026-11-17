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

/** The full program to send to the judge: the hidden parts around the user's code. */
export function composeProgram(parts: Parts, user: string): string {
  const c = COMMENT[parts.lang];
  const body = user.replace(/\s+$/, "");
  const placed = parts.lang === "java"
    ? body.split("\n").map((l) => (l.trim() ? JAVA_INDENT + l : l)).join("\n")
    : body;
  return `${parts.prefix}${c} ${OPEN}\n${placed}\n${c} ${CLOSE}${parts.suffix}`;
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
