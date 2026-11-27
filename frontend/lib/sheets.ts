import type { ProblemSummary } from "./api";

/** The two Striver sheets. A problem belongs to a sheet when it carries that sheet's tag (set by the seed generator). */
export interface Sheet { tag: string; short: string; label: string; full: string; blurb: string }

export const SHEETS: Sheet[] = [
  { tag: "striver-a2z", short: "A2Z", label: "A2Z Sheet", full: "Striver's A2Z DSA Sheet",
    blurb: "Step by step from arrays to DP. Each problem opens with its optimal C++ solution." },
  { tag: "striver-sde", short: "SDE", label: "SDE Sheet", full: "Striver's SDE Sheet",
    blurb: "The classic interview-prep list, arrays to DP." },
];

export const SHEET_TAGS: string[] = SHEETS.map((s) => s.tag);

export const isSheetTag = (tag: string): boolean => SHEET_TAGS.includes(tag);

/** The sheets a problem is on (empty for problems that are on neither). */
export const sheetsOf = (tags: readonly string[]): Sheet[] => SHEETS.filter((s) => tags.includes(s.tag));

/** Topics in the order the sheet shows them (roughly Striver's own order). */
export const TOPIC_ORDER: readonly string[] = [
  "array", "matrix", "string", "linked-list", "stack", "backtracking", "binary-search", "greedy", "heap",
  "tree", "graph", "dynamic-programming", "math", "bit-manipulation",
];
/** Most specific first: a problem tagged array + backtracking belongs under Backtracking, not Array. */
const SPECIFICITY: readonly string[] = [
  "dynamic-programming", "backtracking", "binary-search", "graph", "tree", "linked-list", "heap", "matrix", "stack",
  "greedy", "string", "math", "bit-manipulation", "array",
];

/** The topic a problem is filed under inside a sheet: its most specific known tag, else its first non-sheet tag. */
export const topicOf = (p: Pick<ProblemSummary, "tags">): string =>
  SPECIFICITY.find((t) => p.tags.includes(t)) ?? p.tags.find((t) => !isSheetTag(t)) ?? "other";

/** Sort key for topics: known topics in TOPIC_ORDER first, anything else after them (alphabetical). */
export const topicRank = (topic: string): number => {
  const i = TOPIC_ORDER.indexOf(topic);
  return i >= 0 ? i : TOPIC_ORDER.length;
};
export const compareTopics = (a: string, b: string): number => topicRank(a) - topicRank(b) || a.localeCompare(b);

/** Sheet from a `?sheet=` value such as "a2z", "sde" or the full tag. */
export const sheetFromParam = (v: string | null | undefined): Sheet | undefined => {
  const x = (v ?? "").toLowerCase();
  return SHEETS.find((s) => s.short.toLowerCase() === x || s.tag === x);
};
