"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Point { contest: number; title: string; at: string; rating: number; rank: number; change: number }
interface Bucket { from: number; count: number }
interface RatingView {
  rating: number | null; attended: number; globalRank: number | null; rated: number; topPercent: number | null;
  peak: number | null; history: Point[]; distribution: Bucket[];
}

const fmt = (n: number) => n.toLocaleString("en-US");

/** LeetCode's "Contest Rating" card (rating, global ranking, rating graph) and the "Top %" distribution card. */
export default function ContestRating() {
  const [r, setR] = useState<RatingView | null>(null);
  useEffect(() => { api<RatingView>("/api/profile/rating").then(setR).catch(() => {}); }, []);
  if (!r) return null;

  if (r.rating === null) {
    return (
      <section className="card ratingcard">
        <div className="ratinghead">
          <div><div className="mute">Contest Rating</div><div className="ratingbig">–</div></div>
        </div>
        <p className="mute" style={{ margin: "12px 0 0", fontSize: 14 }}>
          You get a rating after your first weekly contest. <Link href="/contest">Go to Contest</Link>
        </p>
      </section>
    );
  }
  return (
    <>
      <section className="card ratingcard">
        <div className="ratinghead">
          <div><div className="mute">Contest Rating</div><div className="ratingbig">{fmt(r.rating)}</div></div>
          <div>
            <div className="mute">Global Ranking</div>
            <div className="ratingrank"><b>{fmt(r.globalRank ?? 0)}</b><span className="mute">/{fmt(r.rated)}</span></div>
          </div>
        </div>
        <RatingGraph points={r.history} peak={r.peak ?? r.rating} />
      </section>
      <section className="card ratingcard">
        <div className="mute">Top</div>
        <div className="ratingbig">{r.topPercent}%</div>
        <Distribution buckets={r.distribution} mine={r.rating} />
      </section>
    </>
  );
}

function RatingGraph({ points, peak }: { points: Point[]; peak: number }) {
  if (points.length === 0) return null;
  const W = 320, H = 130, PX = 14, PT = 34, PB = 26;
  const ys = points.map((p) => p.rating);
  const lo = Math.min(...ys), hi = Math.max(...ys), span = Math.max(1, hi - lo);
  const x = (i: number) => (points.length === 1 ? W / 2 : PX + (i * (W - 2 * PX)) / (points.length - 1));
  const y = (v: number) => PT + (1 - (v - lo) / span) * (H - PT - PB);
  const path = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.rating).toFixed(1)}`).join(" ");
  const pi = ys.indexOf(peak);
  const px = x(Math.max(0, pi)), py = y(peak);
  const bw = 58, bx = Math.min(W - bw - 2, Math.max(2, px - bw / 2));
  const year = (iso: string) => new Date(iso).getUTCFullYear();
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="ratinggraph" role="img" aria-label={`Rating history, peak ${peak}`}>
      <path d={path} fill="none" stroke="#ffa116" strokeWidth="1.8" strokeLinejoin="round" />
      <circle cx={px} cy={py} r="4.5" fill="#fff" />
      <g>
        <rect x={bx} y={py - 31} width={bw} height="22" rx="5" fill="var(--panel)" stroke="var(--line)" />
        <text x={bx + bw / 2} y={py - 16} textAnchor="middle" fontSize="12" fill="var(--text)">{fmt(peak)}</text>
      </g>
      <text x={PX} y={H - 6} fontSize="12" fill="var(--mute)">{year(points[0].at)}</text>
      <text x={W - PX} y={H - 6} fontSize="12" fill="var(--mute)" textAnchor="end">{year(points[points.length - 1].at)}</text>
    </svg>
  );
}

function Distribution({ buckets, mine }: { buckets: Bucket[]; mine: number }) {
  if (buckets.length === 0) return null;
  const from = buckets[0].from, to = buckets[buckets.length - 1].from;
  const byFrom = new Map(buckets.map((b) => [b.from, b.count]));
  const bars: { from: number; count: number }[] = [];
  for (let f = from; f <= to; f += 100) bars.push({ from: f, count: byFrom.get(f) ?? 0 });
  const max = Math.max(...bars.map((b) => b.count), 1);
  const mineFrom = Math.floor(mine / 100) * 100;
  return (
    <div className="ratingdist" aria-label="Rating distribution">
      {bars.map((b) => (
        <div key={b.from} className={b.from === mineFrom ? "bar me" : "bar"} style={{ height: `${Math.max(4, (b.count / max) * 100)}%` }}
          title={`${b.from}-${b.from + 99}: ${b.count}`} />
      ))}
    </div>
  );
}
