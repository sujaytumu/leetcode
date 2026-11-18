"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import Skeleton from "@/components/Skeleton";
import { DailyCalendar, DailyDay, localDate } from "@/lib/api";
import { swr } from "@/lib/local";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const monthKey = (y: number, m: number) => `${y}-${String(m).padStart(2, "0")}`;

export default function DailyPage() {
  usePageTitle("Daily challenge");
  const now = new Date();
  const [ym, setYm] = useState({ y: now.getFullYear(), m: now.getMonth() + 1 });
  const [cal, setCal] = useState<DailyCalendar | null>(null);
  const [error, setError] = useState("");
  const today = localDate();

  useEffect(() => {
    setCal(null); setError("");
    swr<DailyCalendar>(`/api/daily/calendar?month=${monthKey(ym.y, ym.m)}&today=${today}`, (d) => setCal(d), () => {})
      .catch((e) => setError(e.message));
  }, [ym, today]);

  const shift = (delta: number) => setYm(({ y, m }) => {
    const d = new Date(y, m - 1 + delta, 1);
    return { y: d.getFullYear(), m: d.getMonth() + 1 };
  });
  const atCurrent = ym.y === now.getFullYear() && ym.m === now.getMonth() + 1;
  const lead = new Date(ym.y, ym.m - 1, 1).getDay();
  const byDate = new Map<string, DailyDay>((cal?.days ?? []).map((d) => [d.date, d]));
  const daysInMonth = new Date(ym.y, ym.m, 0).getDate();
  const title = new Date(ym.y, ym.m - 1, 1).toLocaleDateString(undefined, { month: "long", year: "numeric" });

  return (
    <>
      <div className="bar" style={{ marginBottom: 12, gap: 10 }}>
        <h2 style={{ margin: 0 }}>Daily challenge</h2><span className="grow" />
        <button onClick={() => shift(-1)} aria-label="Previous month">‹</button>
        <b style={{ minWidth: 130, textAlign: "center" }}>{title}</b>
        <button onClick={() => shift(1)} disabled={atCurrent} aria-label="Next month">›</button>
      </div>
      {error && <div className="banner err">{error}</div>}
      {!cal && !error && <Skeleton lines={8} />}
      {cal && (
        <>
          <p className="mute" style={{ marginTop: 0 }}>Solved <b style={{ color: "var(--text)" }}>{cal.solved}</b> of {cal.total} daily problems this month.</p>
          <div className="daygrid">
            {WEEKDAYS.map((w) => <div key={w} className="dayhead">{w}</div>)}
            {Array.from({ length: lead }, (_, i) => <div key={`b${i}`} />)}
            {Array.from({ length: daysInMonth }, (_, i) => {
              const date = `${monthKey(ym.y, ym.m)}-${String(i + 1).padStart(2, "0")}`;
              const d = byDate.get(date);
              if (!d) return <div key={date} className="daycell future"><span className="daynum">{i + 1}</span></div>;
              return (
                <Link key={date} href={`/problems/${d.problem.slug}`}
                  className={`daycell${d.solved ? " done" : ""}${date === today ? " today" : ""}`} title={d.problem.title}>
                  <span className="daynum">{i + 1}{d.solved ? " ✓" : ""}</span>
                  <span className="daytitle">{d.problem.title}</span>
                  <span className={d.problem.difficulty} style={{ fontSize: 11 }}>{d.problem.difficulty[0] + d.problem.difficulty.slice(1).toLowerCase()}</span>
                </Link>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
