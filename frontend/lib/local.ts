import { apiWithWake, fetchAllProblems, Page, ProblemSummary } from "./api";
import { catalogUrl, isCatalogPath } from "./catalog";
import type { ProblemDetail } from "./api";

/** Bundled copy of every problem (static file on the CDN): the last resort that renders even if the backend is asleep. */
type Snap = ProblemDetail;
let snapPromise: Promise<Snap[]> | null = null;
function loadSnapshot(): Promise<Snap[]> {
  snapPromise ??= fetch("/problems-snapshot.json").then((r) => (r.ok ? r.json() : [])).catch(() => []);
  return snapPromise;
}
const toSummary = (p: Snap): ProblemSummary => ({
  id: p.id, number: p.number, slug: p.slug, title: p.title, difficulty: p.difficulty, tags: p.tags, status: "TODO", bookmarked: false });

/** Answers the public catalogue paths from the bundled copy; null for anything personal or unknown. */
async function snapshotFallback(path: string): Promise<unknown | null> {
  const snap = await loadSnapshot();
  if (!snap.length) return null;
  if (path === "/api/tags") return Array.from(new Set(snap.flatMap((p) => p.tags))).sort();
  const detail = path.match(/^\/api\/problems\/([^/?]+)$/);
  if (detail) { const p = snap.find((x) => x.slug === detail[1]); return p ? { ...p, status: "TODO", bookmarked: false } : null; }
  if (path.startsWith("/api/problems?")) {
    const q = new URLSearchParams(path.split("?")[1]);
    if (q.get("status") || q.get("bookmarked")) return null; // needs per-user state from the server
    const text = (q.get("q") ?? "").toLowerCase();
    let items = snap.map(toSummary);
    if (text) items = items.filter((p) => p.title.toLowerCase().includes(text));
    if (q.get("difficulty")) items = items.filter((p) => p.difficulty === q.get("difficulty"));
    if (q.get("tag")) items = items.filter((p) => p.tags.includes(q.get("tag")!));
    const sort = q.get("sort"), sign = q.get("dir") === "desc" ? -1 : 1, rank = { EASY: 0, MEDIUM: 1, HARD: 2 };
    if (sort === "title") items = [...items].sort((a, b) => sign * a.title.localeCompare(b.title));
    else if (sort === "difficulty") items = [...items].sort((a, b) => sign * (rank[a.difficulty] - rank[b.difficulty]));
    const size = Number(q.get("size") ?? 20), page = Number(q.get("page") ?? 0);
    return { items: items.slice(page * size, page * size + size), page, size, totalElements: items.length,
      totalPages: Math.max(1, Math.ceil(items.length / size)) } satisfies Page<ProblemSummary>;
  }
  return null;
}

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
    snapshotFallback(path).then((d) => { if (d && !live) onData(d as T, true); }).catch(() => {});
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
  else loadSnapshot().then((snap) => { if (snap.length && !done) onData(snap.map(toSummary), true); });
  let done = false;
  const first = await apiWithWake<Page<ProblemSummary>>("/api/problems?page=0&size=100", onWaiting);
  const items = first.totalPages > 1 ? await fetchAllProblems() : first.items;
  cacheSet("all", items);
  done = true;
  onData(items, false);
}
