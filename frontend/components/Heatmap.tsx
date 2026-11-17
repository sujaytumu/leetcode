"use client";
import { DayCount } from "@/lib/api";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const key = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const level = (n: number) => (n === 0 ? "0" : n < 2 ? "1" : n < 4 ? "2" : "3");

/** LeetCode-style submission calendar: one column per week (Sun–Sat), newest week on the right. */
export default function Heatmap({ calendar, weeks = 53 }: { calendar: DayCount[]; weeks?: number }) {
  const counts = new Map(calendar.map((c) => [c.date, c.count]));
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const start = new Date(today);
  start.setDate(start.getDate() - start.getDay() - 7 * (weeks - 1));

  const labels = [];
  const cells = [];
  let lastMonth = -1;
  for (let w = 0; w < weeks; w++) {
    const first = new Date(start); first.setDate(start.getDate() + w * 7);
    labels.push(<span key={w}>{first.getMonth() !== lastMonth ? MONTHS[first.getMonth()] : ""}</span>);
    lastMonth = first.getMonth();
    for (let r = 0; r < 7; r++) {
      const d = new Date(first); d.setDate(first.getDate() + r);
      const n = counts.get(key(d)) ?? 0;
      const lvl = d > today ? "f" : level(n);
      cells.push(
        <div key={`${w}-${r}`} className={`cell l${lvl}`}
          title={d > today ? "" : `${n} submission${n === 1 ? "" : "s"} on ${key(d)}`} />,
      );
    }
  }
  return (
    <div className="heatwrap">
      <div className="heat-months">{labels}</div>
      <div className="heat" style={{ marginTop: 4 }}>{cells}</div>
    </div>
  );
}
