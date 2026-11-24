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

/** The topic a problem is filed under inside a sheet: its first tag that is not a sheet tag. */
export const topicOf = (p: Pick<ProblemSummary, "tags">): string => p.tags.find((t) => !isSheetTag(t)) ?? "other";

/** Sheet from a `?sheet=` value such as "a2z", "sde" or the full tag. */
export const sheetFromParam = (v: string | null | undefined): Sheet | undefined => {
  const x = (v ?? "").toLowerCase();
  return SHEETS.find((s) => s.short.toLowerCase() === x || s.tag === x);
};
