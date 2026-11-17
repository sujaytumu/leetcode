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
