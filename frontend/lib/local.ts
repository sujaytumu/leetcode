import { apiWithWake, fetchAllProblems, Page, ProblemSummary } from "./api";
import { catalogUrl, isCatalogPath } from "./catalog";

const PREFIX = "lc-cache:";
export function cacheGet<T>(key: string): T | null {
  try { const v = localStorage.getItem(PREFIX + key); return v ? (JSON.parse(v) as T) : null; } catch { return null; }
}
export function cacheSet(key: string, value: unknown) {
  try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch { /* storage full or blocked */ }
}

/**
 * Shows something as fast as possible, then the truth:
 *  1. the last copy this browser received (personalised, instant on repeat visits);
 *  2. otherwise the Vercel-cached public copy, which arrives quickly even while the backend sleeps;
 *  3. finally the live backend response, which always wins and carries the user's own progress.
 */
export async function swr<T>(path: string, onData: (d: T, fromCache: boolean) => void, onWaiting: (n: number) => void) {
  const hit = cacheGet<T>(path);
  if (hit) onData(hit, true);
  let live = false;
  if (!hit && isCatalogPath(path)) {
    fetch(catalogUrl(path), { signal: AbortSignal.timeout(10000) })
      .then((r) => (r.ok && r.status !== 204 ? (r.json() as Promise<T>) : undefined))
      .then((d) => { if (d !== undefined && !live) onData(d, true); })
      .catch(() => { /* the live request below still runs */ });
  }
  const fresh = await apiWithWake<T>(path, onWaiting);
  live = true;
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
