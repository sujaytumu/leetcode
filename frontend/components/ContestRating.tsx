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
export default function ContestRating({ path = "/api/profile/rating" }: { path?: string }) {
  const [r, setR] = useState<RatingView | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => { api<RatingView>(path).then(setR).catch(() => setFailed(true)); }, [path]);
  // While loading or if the server is unreachable, keep the cards (and their graphs) in place with placeholders instead of vanishing.
  const view: RatingView = r ?? { rating: null, attended: 0, globalRank: null, rated: 0, topPercent: null, peak: null, history: [], distribution: [] };

  if (view.rating === null) {
    // No rating yet: still show both LeetCode cards (rating + graph, Top %) with placeholders, so the page keeps its shape.
    const ghost = [8, 14, 26, 44, 70, 100, 82, 56, 36, 22, 14, 9, 6, 4];
    return (
      <div className="card ratingwrap">
        <section className="ratingcard">
          <div className="ratinghead">
            <div><div className="mute">Contest Rating</div><div className="ratingbig">–</div></div>
            <div><div className="mute">Global Ranking</div><div className="ratingrank"><b>–</b></div></div>
            <div><div className="mute">Attended</div><div className="ratingrank"><b>{view.attended}</b></div></div>
          </div>
          <svg viewBox="0 0 320 130" className="ratinggraph ghost" aria-hidden="true">
            <path d="M14,90 L306,90" stroke="var(--mute)" strokeWidth="1.5" strokeDasharray="4 5" fill="none" />
          </svg>
          <p className="mute" style={{ margin: "4px 0 0", fontSize: 14 }}>
            {failed ? "Could not load your rating right now." : <>You get a rating after your first weekly contest. <Link href="/contest">Go to Contest</Link></>}
          </p>
        </section>
        <section className="ratingcard">
          <div className="mute">Top</div>
          <div className="ratingbig">–</div>
          <div className="ratingdist ghost" aria-hidden="true">
            {ghost.map((h, i) => <div key={i} className="bar" style={{ height: `${h}%` }} />)}
          </div>
        </section>
      </div>
    );
  }
  const v = view as RatingView & { rating: number };
  return (
    <div className="card ratingwrap">
      <section className="ratingcard">
        <div className="ratinghead">
          <div><div className="mute">Contest Rating</div><div className="ratingbig">{fmt(v.rating)}</div></div>
          <div>
            <div className="mute">Global Ranking</div>
            <div className="ratingrank"><b>{fmt(v.globalRank ?? 0)}</b><span className="mute">/{fmt(v.rated)}</span></div>
          </div>
          <div><div className="mute">Attended</div><div className="ratingrank"><b>{v.attended}</b></div></div>
        </div>
        <RatingGraph points={v.history} peak={v.peak ?? v.rating} />
      </section>
      <section className="ratingcard">
        <div className="mute">Top</div>
        <div className="ratingbig">{v.topPercent}%</div>
        <Distribution buckets={v.distribution} mine={v.rating} />
      </section>
    </div>
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
  // Mark the highest point actually plotted, so the bubble always sits on the line (the server's peak can span
  // older contests than the graph shows).
  const top = hi;
  const pi = ys.indexOf(top);
  const px = x(Math.max(0, pi)), py = y(top);
  const bw = 58, bx = Math.min(W - bw - 2, Math.max(2, px - bw / 2));
  const year = (iso: string) => new Date(iso).getUTCFullYear();
/** "2025" when the graph spans several years, otherwise "Oct 12" so the axis says something useful. */
const axisLabel = (at: string, first: string, last: string): string => {
  const a = new Date(first), b = new Date(last);
  if (a.getFullYear() !== b.getFullYear()) return String(new Date(at).getFullYear());
  return new Date(at).toLocaleDateString("en-US", { month: "short", day: "numeric" });
};
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="ratinggraph" role="img" aria-label={`Rating history, highest ${hi}`}>
      <path d={path} fill="none" stroke="#ffa116" strokeWidth="1.8" strokeLinejoin="round" />
      {points.map((p, i) => (
        <circle key={i} cx={x(i)} cy={y(p.rating)} r="3" fill={p.change >= 0 ? "var(--ok)" : "var(--bad)"}>
          <title>{`${p.title}: ${p.rating} (${p.change >= 0 ? "+" : ""}${p.change}), rank ${p.rank}`}</title>
        </circle>
      ))}
      <circle cx={px} cy={py} r="4.5" fill="#fff" />
      <g>
        <rect x={bx} y={py - 31} width={bw} height="22" rx="5" fill="var(--panel)" stroke="var(--line)" />
        <path d={`M${px - 5},${py - 9} L${px},${py - 4} L${px + 5},${py - 9}`} fill="var(--panel)" stroke="var(--line)" />
        <rect x={px - 4} y={py - 10} width="8" height="3" fill="var(--panel)" />
        <text x={bx + bw / 2} y={py - 16} textAnchor="middle" fontSize="12" fill="var(--text)">{fmt(top)}</text>
      </g>
      <text x={PX} y={H - 6} fontSize="12" fill="var(--mute)">{axisLabel(points[0].at, points[0].at, points[points.length - 1].at)}</text>
      <text x={W - PX} y={H - 6} fontSize="12" fill="var(--mute)" textAnchor="end">{axisLabel(points[points.length - 1].at, points[0].at, points[points.length - 1].at)}</text>
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
