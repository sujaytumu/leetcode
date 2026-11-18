"use client";
import { DayCount, localDate } from "@/lib/api";
import { weekTotal } from "@/lib/weekly";

/** "This week vs last week" comparison with a seven-day bar strip. */
export default function WeeklySummary({ calendar }: { calendar: DayCount[] }) {
  const today = new Date();
  const prevEnd = new Date(today); prevEnd.setDate(prevEnd.getDate() - 7);
  const thisWeek = weekTotal(calendar, today), lastWeek = weekTotal(calendar, prevEnd);
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today); d.setDate(d.getDate() - (6 - i));
    return { label: d.toLocaleDateString(undefined, { weekday: "short" }), n: calendar.find((c) => c.date === localDate(d))?.count ?? 0 };
  });
  const max = Math.max(1, ...days.map((d) => d.n));
  const diff = thisWeek - lastWeek;
  return (
    <section className="card">
      <div className="bar" style={{ marginBottom: 8 }}>
        <h3 style={{ margin: 0 }}>This week</h3><span className="grow" />
        <span className="mute" style={{ fontSize: 13 }}>
          <b style={{ display: "inline", fontSize: 16 }}>{thisWeek}</b> submissions
          {lastWeek > 0 || thisWeek > 0 ? <> · <span className={diff >= 0 ? "EASY" : "HARD"}>{diff >= 0 ? "+" : ""}{diff}</span> vs last week</> : null}
        </span>
      </div>
      <div className="weekstrip" aria-label="Submissions in the last 7 days">
        {days.map((d, i) => (
          <div key={i} className="wk" title={`${d.label}: ${d.n}`}>
            <div className="wk-bar"><span style={{ height: `${(d.n / max) * 100}%` }} /></div>
            <span className="mute" style={{ fontSize: 11 }}>{d.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
