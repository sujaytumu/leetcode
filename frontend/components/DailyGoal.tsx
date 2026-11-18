"use client";
import { useEffect, useState } from "react";
import { DayCount, localDate } from "@/lib/api";

const KEY = "lc-daily-goal";

/** Daily submission goal kept on this device; progress comes from the profile's activity calendar. */
export default function DailyGoal({ calendar, currentStreak }: { calendar: DayCount[]; currentStreak: number }) {
  const [goal, setGoal] = useState(3);
  useEffect(() => {
    const v = Number(localStorage.getItem(KEY));
    if (v >= 1 && v <= 20) setGoal(v);
  }, []);
  const today = localDate();
  const done = calendar.find((d) => d.date === today)?.count ?? 0;
  const pct = Math.min(100, Math.round((done / goal) * 100));
  const set = (v: number) => {
    const g = Math.min(20, Math.max(1, v));
    setGoal(g);
    try { localStorage.setItem(KEY, String(g)); } catch { /* storage blocked */ }
  };
  const R = 34, C = 2 * Math.PI * R;
  return (
    <section className="card goalcard">
      <div className="bar" style={{ gap: 16 }}>
        <svg width="84" height="84" viewBox="0 0 84 84" role="img" aria-label={`${done} of ${goal} submissions today`}>
          <circle cx="42" cy="42" r={R} fill="none" stroke="var(--cell)" strokeWidth="8" />
          <circle cx="42" cy="42" r={R} fill="none" stroke={done >= goal ? "var(--easy)" : "var(--accent)"} strokeWidth="8"
            strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)} transform="rotate(-90 42 42)" />
          <text x="42" y="47" textAnchor="middle" fontSize="16" fontWeight="700" fill="var(--text)">{done}/{goal}</text>
        </svg>
        <div className="grow">
          <h3 style={{ margin: 0 }}>Daily goal</h3>
          <div className="mute" style={{ fontSize: 13 }}>
            {done >= goal ? "Goal reached. Nice work." : `${goal - done} more submission${goal - done === 1 ? "" : "s"} to hit today's goal.`}
            {currentStreak > 0 && <> 🔥 {currentStreak}-day streak</>}
          </div>
          <div className="bar" style={{ marginTop: 8 }}>
            <button aria-label="Lower goal" onClick={() => set(goal - 1)}>−</button>
            <span className="mute">Goal: <b style={{ display: "inline", fontSize: 14 }}>{goal}</b> / day</span>
            <button aria-label="Raise goal" onClick={() => set(goal + 1)}>+</button>
          </div>
        </div>
      </div>
    </section>
  );
}
