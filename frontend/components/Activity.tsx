"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Profile, profilePath } from "@/lib/api";
import { swr } from "@/lib/local";
import Heatmap from "./Heatmap";

/** Home-page activity strip; all numbers come from the server's submission history. */
export default function Activity() {
  const [p, setP] = useState<Profile | null>(null);
  useEffect(() => { swr<Profile>(profilePath(), (d) => setP(d), () => {}).catch(() => {}); }, []);
  if (!p) return null;
  return (
    <div className="card activity">
      <div className="bar" style={{ flexWrap: "wrap", gap: 16 }}>
        <span><b>🔥 {p.currentStreak}</b> <span className="mute">day streak</span></span>
        <span><b>{p.maxStreak}</b> <span className="mute">max streak</span></span>
        <span><b>{p.activeDays}</b> <span className="mute">active days</span></span>
        <span className="grow" />
        <Link href="/profile" className="mute" style={{ fontSize: 13 }}>View profile →</Link>
      </div>
      <Heatmap calendar={p.calendar} weeks={26} />
    </div>
  );
}
