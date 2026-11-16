import { apiWithWake, fetchAllProblems, Page, ProblemSummary } from "./api";

const PREFIX = "lc-cache:";
export function cacheGet<T>(key: string): T | null {
  try { const v = localStorage.getItem(PREFIX + key); return v ? (JSON.parse(v) as T) : null; } catch { return null; }
}
export function cacheSet(key: string, value: unknown) {
  try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch { /* storage full or blocked */ }
}

/** Stale-while-revalidate: shows the last copy received from the server at once, then replaces it with fresh server data. */
export async function swr<T>(path: string, onData: (d: T, fromCache: boolean) => void, onWaiting: (n: number) => void) {
  const hit = cacheGet<T>(path);
  if (hit) onData(hit, true);
  const fresh = await apiWithWake<T>(path, onWaiting);
  cacheSet(path, fresh);
  onData(fresh, false);
}

export async function loadAll(onData: (items: ProblemSummary[], fromCache: boolean) => void, onWaiting: (n: number) => void) {
  const hit = cacheGet<ProblemSummary[]>("all");
  if (hit) onData(hit, true);
  const first = await apiWithWake<Page<ProblemSummary>>("/api/problems?page=0&size=100", onWaiting);
  const items = first.totalPages > 1 ? await fetchAllProblems() : first.items;
  cacheSet("all", items);
  onData(items, false);
}

const AKEY = "lc-activity";
export const dayKey = (d = new Date()) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
export function getActivity(): Record<string, number> {
  try { return JSON.parse(localStorage.getItem(AKEY) ?? "{}"); } catch { return {}; }
}
export function recordAccepted() {
  try { const a = getActivity(); const k = dayKey(); a[k] = (a[k] ?? 0) + 1; localStorage.setItem(AKEY, JSON.stringify(a)); } catch { /* ignore */ }
}
export function streaks(a: Record<string, number>) {
  let current = 0;
  const d = new Date();
  if (!a[dayKey(d)]) d.setDate(d.getDate() - 1); // today may not be solved yet
  while (a[dayKey(d)]) { current++; d.setDate(d.getDate() - 1); }
  const days = Object.keys(a).filter((k) => a[k] > 0).sort();
  let longest = 0, run = 0;
  let prev: Date | null = null;
  for (const k of days) {
    const [y, m, dd] = k.split("-").map(Number);
    const dt = new Date(y, m - 1, dd);
    run = prev && Math.round((dt.getTime() - prev.getTime()) / 86400000) === 1 ? run + 1 : 1;
    longest = Math.max(longest, run);
    prev = dt;
  }
  return { current, longest, total: days.length };
}
