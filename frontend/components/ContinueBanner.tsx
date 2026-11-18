"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

export const LAST_KEY = "lc-last-problem";
interface Last { slug: string; title: string; at: number }

/** Remembers the problem being worked on (call from the workspace). */
export function rememberProblem(slug: string, title: string) {
  try { localStorage.setItem(LAST_KEY, JSON.stringify({ slug, title, at: Date.now() } satisfies Last)); } catch { /* storage blocked */ }
}

/** "Continue where you left off" shortcut on the home page; hidden after a solve or after a week. */
export default function ContinueBanner() {
  const [last, setLast] = useState<Last | null>(null);
  useEffect(() => {
    try {
      const v = JSON.parse(localStorage.getItem(LAST_KEY) ?? "null") as Last | null;
      if (v?.slug && Date.now() - v.at < 7 * 86400000) setLast(v);
    } catch { /* corrupt */ }
  }, []);
  if (!last) return null;
  return (
    <div className="banner" style={{ marginBottom: 12 }}>
      <span>Continue where you left off:</span>
      <Link href={`/problems/${last.slug}`}><b>{last.title}</b></Link>
      <span className="grow" />
      <button type="button" aria-label="Dismiss" onClick={() => { try { localStorage.removeItem(LAST_KEY); } catch {} setLast(null); }}>✕</button>
    </div>
  );
}
