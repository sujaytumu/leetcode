// Remembers the problem list's filters and sort order between visits (the search text is deliberately not kept).
export const FILTER_KEY = "lc-list-filters";

export type ListFilters = {
  difficulty: string; tag: string; status: string; sort: string; dir: "asc" | "desc"; bookmarked: boolean;
};

const short = (v: unknown): string | undefined => (typeof v === "string" && v.length <= 40 ? v : undefined);
const DIFFICULTIES = new Set(["", "EASY", "MEDIUM", "HARD"]);
const SORTS = new Set(["", "title", "acceptance", "difficulty"]);

/** Reads whatever was saved; anything missing, malformed or unexpected is simply left out. */
export function parseFilters(raw: string | null): Partial<ListFilters> {
  if (!raw) return {};
  let v: unknown;
  try { v = JSON.parse(raw); } catch { return {}; }
  if (typeof v !== "object" || v === null) return {};
  const o = v as Record<string, unknown>;
  const out: Partial<ListFilters> = {};
  const difficulty = short(o.difficulty), tag = short(o.tag), status = short(o.status), sort = short(o.sort);
  if (difficulty !== undefined && DIFFICULTIES.has(difficulty)) out.difficulty = difficulty;
  if (tag !== undefined) out.tag = tag;
  if (status !== undefined) out.status = status;
  if (sort !== undefined && SORTS.has(sort)) out.sort = sort;
  if (o.dir === "asc" || o.dir === "desc") out.dir = o.dir;
  if (typeof o.bookmarked === "boolean") out.bookmarked = o.bookmarked;
  return out;
}
