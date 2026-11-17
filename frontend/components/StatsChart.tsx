"use client";
import type { Distribution } from "@/lib/api";

/** Histogram of how other accepted submissions measured, with the viewer's own bucket highlighted (as on LeetCode). */
export default function StatsChart({ dist, format, label }: { dist: Distribution; format: (v: number) => string; label: string }) {
  const W = 320, H = 96, pad = 4, base = H - 16;
  const max = Math.max(1, ...dist.bins.map((b) => b.count));
  const bw = (W - pad * 2) / dist.bins.length;
  const first = dist.bins[0], last = dist.bins[dist.bins.length - 1];
  return (
    <svg className="statschart" viewBox={`0 0 ${W} ${H}`} role="img" preserveAspectRatio="xMidYMid meet"
      aria-label={`${label} distribution: yours is ${format(dist.value)}${dist.beatsPercent != null ? `, faster than ${dist.beatsPercent}% of submissions` : ""}`}>
      <line x1={pad} x2={W - pad} y1={base} y2={base} stroke="var(--line)" />
      {dist.bins.map((b, i) => {
        const h = b.count === 0 ? 0 : Math.max(3, (b.count / max) * (base - 8));
        const mine = i === dist.userBin;
        return (
          <g key={i}>
            <rect x={pad + i * bw + 1.5} y={base - h} width={Math.max(1, bw - 3)} height={h} rx="2"
              fill={mine ? "var(--accent)" : "var(--cell)"} stroke={mine ? "none" : "var(--line)"}>
              <title>{`${format(b.from)}–${format(b.to)}: ${b.count} submission${b.count === 1 ? "" : "s"}`}</title>
            </rect>
            {mine && <text x={pad + i * bw + bw / 2} y={base - h - 3} textAnchor="middle" fontSize="9" fill="var(--accent)">you</text>}
          </g>
        );
      })}
      <text x={pad} y={H - 3} fontSize="9" fill="var(--mute)">{format(first.from)}</text>
      <text x={W - pad} y={H - 3} fontSize="9" fill="var(--mute)" textAnchor="end">{format(last.to)}</text>
    </svg>
  );
}
