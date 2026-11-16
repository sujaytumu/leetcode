"use client";
import { useEffect, useState } from "react";
import { dayKey, getActivity, streaks } from "@/lib/local";

const WEEKS = 20;

export default function Activity() {
  const [a, setA] = useState<Record<string, number> | null>(null);
  useEffect(() => { setA(getActivity()); }, []);
  if (!a) return null;
  const s = streaks(a);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const start = new Date(today); start.setDate(start.getDate() - start.getDay() - 7 * (WEEKS - 1));
  const cells = [];
  for (let i = 0; i < WEEKS * 7; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i);
    const n = a[dayKey(d)] ?? 0;
    const lvl = d > today ? "f" : n === 0 ? "0" : n < 2 ? "1" : n < 4 ? "2" : "3";
    cells.push(<div key={i} className={`cell l${lvl}`} title={`${dayKey(d)}: ${n} accepted`} />);
  }
  return (
    <div className="activity">
      <div className="bar" style={{ flexWrap: "wrap", gap: 16 }}>
        <span><b>🔥 {s.current}</b> <span className="mute">day streak</span></span>
        <span><b>{s.longest}</b> <span className="mute">longest</span></span>
        <span><b>{s.total}</b> <span className="mute">active days</span></span>
        <span className="mute" style={{ fontSize: 12 }}>accepted submissions on this device</span>
      </div>
      <div className="heat">{cells}</div>
    </div>
  );
}
