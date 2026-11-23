/** Recently opened problems, newest first; kept on this device for the command palette. */
const KEY = "lc-recent";
export const RECENT_MAX = 8;
export interface RecentItem { slug: string; title: string; number?: number | null; difficulty?: string }

export function getRecent(): RecentItem[] {
  try {
    const v = JSON.parse(localStorage.getItem(KEY) ?? "[]");
    return Array.isArray(v) ? v.filter((x) => x && typeof x.slug === "string" && typeof x.title === "string") : [];
  } catch { return []; }
}

/** Moves the problem to the front, drops duplicates and caps the list. */
export function pushRecent(item: RecentItem): RecentItem[] {
  const next = [item, ...getRecent().filter((x) => x.slug !== item.slug)].slice(0, RECENT_MAX);
  try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* storage blocked */ }
  return next;
}
