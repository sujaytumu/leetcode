/** Solve times recorded from the workspace timer when a submission is accepted; kept on this device. */
const KEY = "lc-times";
export interface TimeRecord { best: number; last: number; runs: number }
type Store = Record<string, TimeRecord>;

function read(): Store {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "{}") as Store; } catch { return {}; }
}
export function getTime(slug: string): TimeRecord | null { return read()[slug] ?? null; }

/** Saves one timed accepted solve and returns the updated record plus whether it beat the previous best. */
export function recordTime(slug: string, secs: number): { rec: TimeRecord; improved: boolean } {
  const s = read(), prev = s[slug];
  const rec: TimeRecord = { best: prev ? Math.min(prev.best, secs) : secs, last: secs, runs: (prev?.runs ?? 0) + 1 };
  s[slug] = rec;
  try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* storage blocked */ }
  return { rec, improved: !!prev && secs < prev.best };
}

export const fmtSecs = (n: number) => `${String(Math.floor(n / 60)).padStart(2, "0")}:${String(n % 60).padStart(2, "0")}`;
