"use client";
import { useEffect, useState } from "react";
import { Profile, profilePath } from "@/lib/api";
import { swr } from "@/lib/local";

const KEY = "lc-weekly-goal";
const pad = (n: number) => String(n).padStart(2, "0");
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

/** Monday of the current week, as YYYY-MM-DD in the browser's calendar. */
function weekStart(now = new Date()): string {
  const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return ymd(d);
}

/** Weekly practice goal: active days this week (Mon-Sun) against a target the user picks. */
export default function WeeklyGoal() {
  const [p, setP] = useState<Profile | null>(null);
  const [goal, setGoal] = useState(5);
  useEffect(() => {
    swr<Profile>(profilePath(), (d) => setP(d), () => {}).catch(() => {});
    try { const g = Number(localStorage.getItem(KEY)); if (g >= 1 && g <= 7) setGoal(g); } catch { /* storage blocked */ }
  }, []);
  if (!p) return null;

  const start = weekStart();
  const days = p.calendar.filter((c) => c.date >= start && c.count > 0).length;
  const subs = p.calendar.filter((c) => c.date >= start).reduce((s, c) => s + c.count, 0);
  const pct = Math.min(100, Math.round((days / goal) * 100));
  const done = days >= goal;
  const R = 26, C = 2 * Math.PI * R;
  const change = (v: number) => { setGoal(v); try { localStorage.setItem(KEY, String(v)); } catch { /* ignore */ } };

  return (
    <div className="card weekly">
      <svg width="64" height="64" viewBox="0 0 64 64" role="img" aria-label={`${days} of ${goal} active days this week`}>
        <circle cx="32" cy="32" r={R} fill="none" stroke="var(--line)" strokeWidth="6" />
        <circle cx="32" cy="32" r={R} fill="none" stroke={done ? "var(--easy, #2cbb5d)" : "var(--accent, #ffa116)"} strokeWidth="6"
          strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)} transform="rotate(-90 32 32)" />
        <text x="32" y="37" textAnchor="middle" fontSize="15" fontWeight="700" fill="currentColor">{days}/{goal}</text>
      </svg>
      <div style={{ minWidth: 0 }}>
        <b style={{ fontSize: 15 }}>{done ? "Weekly goal reached 🎉" : "Weekly goal"}</b>
        <div className="mute" style={{ fontSize: 13 }}>{days} active {days === 1 ? "day" : "days"} · {subs} submission{subs === 1 ? "" : "s"} since Monday</div>
        <label className="mute" style={{ fontSize: 12 }}>Target{" "}
          <select value={goal} onChange={(e) => change(Number(e.target.value))} aria-label="Weekly goal in days">
            {[1, 2, 3, 4, 5, 6, 7].map((n) => <option key={n} value={n}>{n} days / week</option>)}
          </select>
        </label>
      </div>
    </div>
  );
}
