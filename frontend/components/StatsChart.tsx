"use client";
import { useState } from "react";
import type { Distribution } from "@/lib/api";

/** LeetCode-style histogram: share of accepted submissions per bucket (y axis in %), hover tooltip, your bucket marked, overview strip underneath. */
export default function StatsChart({ dist, format, label, noun }: { dist: Distribution; format: (v: number) => string; label: string; noun?: string }) {
  const [hover, setHover] = useState<number | null>(null);
  const W = 640, H = 240, left = 52, right = 8, top = 12, base = H - 28;
  const total = Math.max(1, dist.bins.reduce((n, b) => n + b.count, 0));
  const pct = dist.bins.map((b) => (b.count / total) * 100);
  const yMax = Math.max(20, Math.ceil(Math.max(...pct) / 20) * 20);
  const ticks = Array.from({ length: yMax / 20 + 1 }, (_, i) => i * 20);
  const bw = (W - left - right) / dist.bins.length;
  const x = (i: number) => left + i * bw;
  const y = (p: number) => base - (p / yMax) * (base - top);
  const first = dist.bins[0], last = dist.bins[dist.bins.length - 1];
  const labelIdx = [Math.round(dist.bins.length * 0.25), Math.round(dist.bins.length * 0.5), Math.round(dist.bins.length * 0.75)];
  const hb = hover != null ? dist.bins[hover] : null;
  const unit = noun ?? label.toLowerCase();
  return (
    <div className="lcchart">
      <div className="lcchart-plot">
        <svg className="statschart" viewBox={`0 0 ${W} ${H}`} role="img" preserveAspectRatio="xMidYMid meet"
          aria-label={`${label} distribution: yours is ${format(dist.value)}${dist.beatsPercent != null ? `, beats ${dist.beatsPercent}% of submissions` : ""}`}
          onMouseLeave={() => setHover(null)}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={left} x2={W - right} y1={y(t)} y2={y(t)} stroke="var(--line)" strokeWidth="1" />
              <text x={left - 8} y={y(t) + 4} fontSize="14" fill="var(--mute)" textAnchor="end">{t}%</text>
            </g>
          ))}
          {dist.bins.map((b, i) => (
            <g key={i} onMouseEnter={() => setHover(i)} onTouchStart={() => setHover(i)}>
              <rect x={x(i)} y={top} width={bw} height={base - top} fill="transparent" />
              <rect x={x(i) + bw * 0.18} y={y(pct[i])} width={Math.max(2, bw * 0.64)} height={base - y(pct[i])} rx="1.5"
                fill={i === dist.userBin ? "#3b9dff" : "#1a7be0"} opacity={hover == null || hover === i || i === dist.userBin ? 1 : 0.75} />
            </g>
          ))}
          {dist.userBin >= 0 && dist.userBin < dist.bins.length && (
            <g aria-hidden="true">
              <circle cx={x(dist.userBin) + bw / 2} cy={Math.min(y(pct[dist.userBin]) - 4, base - 12)} r="11" fill="var(--panel)" stroke="#3b9dff" strokeWidth="2" />
              <text x={x(dist.userBin) + bw / 2} cy="0" y={Math.min(y(pct[dist.userBin]) - 4, base - 12) + 3.5} fontSize="11" fontWeight="700" textAnchor="middle" fill="#3b9dff">you</text>
            </g>
          )}
          {labelIdx.map((i) => i > 0 && i < dist.bins.length && (
            <text key={i} x={x(i)} y={H - 8} fontSize="14" fill="var(--mute)" textAnchor="middle">{format(dist.bins[i].from)}</text>
          ))}
        </svg>
        {hb && hover != null && (
          <div className="lctip" style={{ left: `${Math.min(78, Math.max(4, ((x(hover) + bw / 2) / W) * 100))}%`, top: 8 }} role="status">
            {pct[hover].toFixed(2)}% of solutions used {format(hb.from)} of {unit}
          </div>
        )}
      </div>
      <svg className="lcmini" viewBox={`0 0 ${W} 46`} aria-hidden="true">
        <rect x={left} y="0" width={W - left - right} height="46" rx="6" fill="var(--cell)" />
        {dist.bins.map((b, i) => <rect key={i} x={x(i) + bw * 0.2} y={40 - Math.max(2, (pct[i] / yMax) * 34)} width={Math.max(2, bw * 0.6)} height={Math.max(2, (pct[i] / yMax) * 34)} fill="var(--mute)" opacity=".55" />)}
        {labelIdx.map((i) => i > 0 && i < dist.bins.length && <text key={i} x={x(i)} y="30" fontSize="14" fill="var(--text)" opacity=".8" textAnchor="middle">{format(dist.bins[i].from)}</text>)}
      </svg>
      <div className="sr-only">{format(first.from)} to {format(last.to)}</div>
    </div>
  );
}
