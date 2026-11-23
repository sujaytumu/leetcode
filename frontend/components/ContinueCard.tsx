"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

export const LAST_KEY = "lc-last-problem";
export interface LastProblem { slug: string; title: string; at: number }

/** Remembers the problem being worked on so the home page can offer to resume it. */
export function rememberProblem(slug: string, title: string) {
  try { localStorage.setItem(LAST_KEY, JSON.stringify({ slug, title, at: Date.now() } satisfies LastProblem)); } catch { /* storage blocked */ }
}

export default function ContinueCard() {
  const [last, setLast] = useState<LastProblem | null>(null);
  useEffect(() => {
    try {
      const v = JSON.parse(localStorage.getItem(LAST_KEY) ?? "null") as LastProblem | null;
      if (v && v.slug && v.title) setLast(v);
    } catch { /* corrupt entry */ }
  }, []);
  if (!last) return null;
  const hours = Math.floor((Date.now() - last.at) / 3600000);
  const when = hours < 1 ? "less than an hour ago" : hours < 24 ? `${hours}h ago` : `${Math.floor(hours / 24)}d ago`;
  return (
    <div className="card daily">
      <div>
        <span className="mute">Continue where you left off · {when}</span>
        <div><Link href={`/problems/${last.slug}`}><b style={{ display: "inline", fontSize: 15 }}>{last.title}</b></Link></div>
      </div>
      <span className="grow" />
      <Link href={`/problems/${last.slug}`} className="navbtn">Resume →</Link>
    </div>
  );
}
