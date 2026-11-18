"use client";
import { useEffect, useRef } from "react";
import { DayCount } from "@/lib/api";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const key = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const level = (n: number) => (n === 0 ? "0" : n < 2 ? "1" : n < 4 ? "2" : n < 7 ? "3" : "4");

/**
 * LeetCode-style submission calendar: one block per month (weeks as columns, Sunday on top), the month name under
 * each block. Shows the last 12 months, or a whole calendar year when {@code year} is given. {@code weeks} trims the
 * range for compact uses (about 4.3 weeks per month). It opens scrolled to the newest month.
 */
export default function Heatmap({ calendar, weeks = 53, year }: { calendar: DayCount[]; weeks?: number; year?: number }) {
  const counts = new Map(calendar.map((c) => [c.date, c.count]));
  const today = new Date(); today.setHours(0, 0, 0, 0);

  const months: { y: number; m: number }[] = [];
  if (year) {
    for (let m = 0; m < 12; m++) months.push({ y: year, m });
  } else {
    const n = Math.max(1, Math.min(12, Math.round(weeks / 4.4)));
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
      months.push({ y: d.getFullYear(), m: d.getMonth() });
    }
  }

  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { if (ref.current && !year) ref.current.scrollLeft = ref.current.scrollWidth; }, [year, calendar]);

  return (
    <div className="hm" ref={ref}>
      {months.map(({ y, m }) => {
        const first = new Date(y, m, 1);
        const days = new Date(y, m + 1, 0).getDate();
        const lead = first.getDay();
        const cells = [];
        for (let i = 0; i < lead; i++) cells.push(<div key={`s${i}`} className="cell lf" />);
        for (let day = 1; day <= days; day++) {
          const d = new Date(y, m, day);
          const n = counts.get(key(d)) ?? 0;
          const future = d > today;
          cells.push(
            <div key={day} className={`cell l${future ? "f" : level(n)}`}
              title={future ? "" : `${n} submission${n === 1 ? "" : "s"} on ${key(d)}`} />,
          );
        }
        return (
          <div key={`${y}-${m}`} className="hm-month">
            <div className="hm-grid">{cells}</div>
            <div className="hm-label">{MONTHS[m]}</div>
          </div>
        );
      })}
    </div>
  );
}
