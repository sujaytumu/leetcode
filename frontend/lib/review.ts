/** Spaced repetition on this device: after each successful review the next one is pushed further out. */
export const STEPS = [1, 3, 7, 14, 30, 60]; // days after the previous review (stage 0 = after the first accepted solve)
const KEY = "lc-review";
const DAY = 86400000;

export interface ReviewState { stage: number; last: string } // last = ISO time of the last review (or first solve)
type Store = Record<string, ReviewState>;

function read(): Store {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "{}") as Store; } catch { return {}; }
}
function write(s: Store) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* storage blocked */ } }

export const loadReviews = read;

/** When the problem is next due, given its saved state or the time of its first accepted solve. */
export function dueAt(firstSolve: string, st?: ReviewState): number {
  const stage = st?.stage ?? 0;
  const base = new Date(st?.last ?? firstSolve).getTime();
  return base + STEPS[Math.min(stage, STEPS.length - 1)] * DAY;
}

export function markReviewed(slug: string, remembered: boolean, firstSolve: string) {
  const s = read(), cur = s[slug];
  const stage = remembered ? Math.min((cur?.stage ?? 0) + 1, STEPS.length - 1) : 0;
  s[slug] = { stage, last: new Date().toISOString() };
  void firstSolve;
  write(s);
}

export function daysUntil(ts: number, now = Date.now()): number { return Math.ceil((ts - now) / DAY); }
