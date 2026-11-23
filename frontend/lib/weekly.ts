export interface DayLike { date: string; count: number }

/** Local calendar date as YYYY-MM-DD, matching the activity calendar's keys. */
export function dayKey(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Sum of submissions in the 7 days ending on `end` (inclusive). */
export function weekTotal(calendar: DayLike[], end: Date): number {
  const keys = new Set<string>();
  for (let i = 0; i < 7; i++) { const d = new Date(end); d.setDate(d.getDate() - i); keys.add(dayKey(d)); }
  return calendar.filter((c) => keys.has(c.date)).reduce((n, c) => n + c.count, 0);
}
