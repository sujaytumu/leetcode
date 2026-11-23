"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

/** LeetCode's flame + number in the top bar: your current daily streak, linking to the daily challenge. */
export default function StreakChip() {
  const [n, setN] = useState<number | null>(null);
  useEffect(() => {
    // The full profile is a heavy request, so reuse a value fetched in the last few minutes instead of asking on every page load.
    const KEY = "lc-streak";
    try {
      const c = JSON.parse(sessionStorage.getItem(KEY) ?? "null") as { n: number; at: number } | null;
      if (c) { setN(c.n); if (Date.now() - c.at < 5 * 60_000) return; }
    } catch { /* storage blocked */ }
    api<{ currentStreak?: number }>("/api/profile").then((p) => {
      const v = p.currentStreak ?? 0; setN(v);
      try { sessionStorage.setItem(KEY, JSON.stringify({ n: v, at: Date.now() })); } catch { /* storage blocked */ }
    }).catch(() => setN((cur) => cur ?? 0));
  }, []);
  return (
    <Link href="/daily" className="streakchip" title="Daily challenge streak" aria-label={`Daily challenge streak: ${n ?? 0}`}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 3c.5 3-1.5 4.5-3 6.5C7.5 11.5 7 13 7 14.5a5 5 0 0 0 10 0c0-2-1-3.3-2-4.5-.3 1.2-1 2-2 2 .8-2.5.5-6-1-9Z" />
      </svg>
      <span>{n ?? 0}</span>
    </Link>
  );
}
