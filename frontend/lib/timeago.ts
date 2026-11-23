const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 86400], ["month", 30 * 86400], ["week", 7 * 86400], ["day", 86400], ["hour", 3600], ["minute", 60],
];

/** "3 hours ago" / "just now", the way LeetCode lists submission times. */
export function timeAgo(from: string | number | Date, now: number = Date.now(), locale?: string): string {
  const secs = Math.round((now - new Date(from).getTime()) / 1000);
  if (!Number.isFinite(secs)) return "";
  if (secs < 45) return "just now";
  const fmt = new Intl.RelativeTimeFormat(locale ?? "en", { numeric: "always" });
  for (const [unit, size] of UNITS) {
    if (secs >= size) return fmt.format(-Math.floor(secs / size), unit);
  }
  return fmt.format(-1, "minute");
}
