import { apiWithWake, fetchAllProblems, Page, ProblemDetail, ProblemSummary } from "./api";

const PREFIX = "lc-cache:";
export function cacheGet<T>(key: string): T | null {
  try { const v = localStorage.getItem(PREFIX + key); return v ? (JSON.parse(v) as T) : null; } catch { return null; }
}
export function cacheSet(key: string, value: unknown) {
  try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch { /* storage full or blocked */ }
}

/** Bundled copy of every problem (served from the CDN), so pages render before the free backend has woken up. */
interface Snap extends ProblemDetail {}
let snapPromise: Promise<Snap[]> | null = null;
function loadSnapshot(): Promise<Snap[]> {
  snapPromise ??= fetch("/problems-snapshot.json").then((r) => (r.ok ? r.json() : [])).catch(() => []);
  return snapPromise;
}
const toSummary = (p: Snap): ProblemSummary => ({
  id: p.id, slug: p.slug, title: p.title, difficulty: p.difficulty, tags: p.tags, status: "TODO", bookmarked: false });

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
    const size = Number(q.get("size") ?? 20), page = Number(q.get("page") ?? 0);
    return { items: items.slice(page * size, page * size + size), page, size, totalElements: items.length,
      totalPages: Math.max(1, Math.ceil(items.length / size)) } satisfies Page<ProblemSummary>;
  }
  return null;
}

/** Stale-while-revalidate: shows a saved copy (or the bundled snapshot) at once, then replaces it with fresh server data. */
export async function swr<T>(path: string, onData: (d: T, fromCache: boolean) => void, onWaiting: (n: number) => void) {
  let done = false;
  const hit = cacheGet<T>(path);
  if (hit) onData(hit, true);
  else snapshotFallback(path).then((s) => { if (s && !done) onData(s as T, true); }).catch(() => {});
  try {
    const fresh = await apiWithWake<T>(path, onWaiting);
    cacheSet(path, fresh);
    done = true;
    onData(fresh, false);
  } finally { done = true; }
}

export async function loadAll(onData: (items: ProblemSummary[], fromCache: boolean) => void, onWaiting: (n: number) => void) {
  let done = false;
  const hit = cacheGet<ProblemSummary[]>("all");
  if (hit) onData(hit, true);
  else loadSnapshot().then((snap) => { if (snap.length && !done) onData(snap.map(toSummary), true); });
  const first = await apiWithWake<Page<ProblemSummary>>("/api/problems?page=0&size=100", onWaiting);
  const items = first.totalPages > 1 ? await fetchAllProblems() : first.items;
  cacheSet("all", items);
  done = true;
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
