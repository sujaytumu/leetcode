export interface DayLite { date: string; solved: boolean }

/** Consecutive solved days ending today (or yesterday, so an unsolved today does not break a streak yet). */
export function dailyStreak(days: DayLite[], today: string): number {
  const solved = new Set(days.filter((d) => d.solved).map((d) => d.date));
  const step = (iso: string, delta: number) => {
    const d = new Date(`${iso}T00:00:00`); d.setDate(d.getDate() + delta);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  };
  let cursor = solved.has(today) ? today : step(today, -1);
  let n = 0;
  while (solved.has(cursor)) { n++; cursor = step(cursor, -1); }
  return n;
}
