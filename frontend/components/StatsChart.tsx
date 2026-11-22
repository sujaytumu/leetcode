"use client";
import { useRef, useState } from "react";
import type { Distribution } from "@/lib/api";

/** LeetCode-style histogram: share of accepted submissions per bucket (y axis in %), hover tooltip, your bucket marked, overview strip underneath. */
export default function StatsChart({ dist, format, label, noun }: { dist: Distribution; format: (v: number) => string; label: string; noun?: string }) {
  const [hover, setHover] = useState<number | null>(null);
  const n = dist.bins.length;
  const [range, setRange] = useState<[number, number]>([0, n - 1]);
  const drag = useRef<{ kind: "lo" | "hi" | "move"; start: number; r: [number, number] } | null>(null);
  const [lo, hi] = range;
  const W = 640, H = 240, left = 52, right = 8, top = 12, base = H - 28;
  const total = Math.max(1, dist.bins.reduce((n, b) => n + b.count, 0));
  const allPct = dist.bins.map((b) => (b.count / total) * 100);
  const bins = dist.bins.slice(lo, hi + 1);
  const pct = allPct.slice(lo, hi + 1);
  const userIdx = dist.userBin - lo;
  const yMax = Math.max(20, Math.ceil(Math.max(...pct) / 20) * 20);
  const yMaxAll = Math.max(20, Math.ceil(Math.max(...allPct) / 20) * 20);
  const ticks = Array.from({ length: yMax / 20 + 1 }, (_, i) => i * 20);
  const bw = (W - left - right) / bins.length;
  const mbw = (W - left - right) / n;
  const x = (i: number) => left + i * bw;
  const y = (p: number) => base - (p / yMax) * (base - top);
  const first = dist.bins[0], last = dist.bins[n - 1];
  const labelIdx = [0.25, 0.5, 0.75].map((f) => Math.round(bins.length * f));
  const mLabelIdx = [0.25, 0.5, 0.75].map((f) => Math.round(n * f));
  const hb = hover != null ? bins[hover] : null;
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
          {bins.map((b, i) => (
            <g key={i} onMouseEnter={() => setHover(i)} onTouchStart={() => setHover(i)}>
              <rect x={x(i)} y={top} width={bw} height={base - top} fill="transparent" />
              <rect x={x(i) + bw * 0.18} y={y(pct[i])} width={Math.max(2, bw * 0.64)} height={base - y(pct[i])} rx="1.5"
                fill={i === userIdx ? "#3b9dff" : "#1a7be0"} opacity={hover == null || hover === i || i === userIdx ? 1 : 0.75} />
            </g>
          ))}
          {userIdx >= 0 && userIdx < bins.length && (
            <g aria-hidden="true">
              <circle cx={x(userIdx) + bw / 2} cy={Math.min(y(pct[userIdx]) - 4, base - 12)} r="11" fill="var(--panel)" stroke="#3b9dff" strokeWidth="2" />
              <text x={x(userIdx) + bw / 2} cy="0" y={Math.min(y(pct[userIdx]) - 4, base - 12) + 3.5} fontSize="11" fontWeight="700" textAnchor="middle" fill="#3b9dff">you</text>
            </g>
          )}
          {labelIdx.map((i) => i > 0 && i < bins.length && (
            <text key={i} x={x(i)} y={H - 8} fontSize="14" fill="var(--mute)" textAnchor="middle">{format(bins[i].from)}</text>
          ))}
        </svg>
        {hb && hover != null && (
          <div className="lctip" style={{ left: `${Math.min(78, Math.max(4, ((x(hover) + bw / 2) / W) * 100))}%`, top: 8 }} role="status">
            {pct[hover].toFixed(2)}% of solutions used {format(hb.from)} of {unit}
          </div>
        )}
      </div>
      <svg className="lcmini" viewBox={`0 0 ${W} 46`} role="slider" aria-label="Zoom range" aria-valuemin={0} aria-valuemax={n - 1} aria-valuenow={lo}
        onPointerMove={(e) => {
          const d = drag.current; if (!d) return;
          const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect();
          const idx = Math.round(((e.clientX - r.left) / r.width * W - left) / mbw);
          const c = (v: number) => Math.max(0, Math.min(n - 1, v));
          if (d.kind === "lo") setRange([Math.min(c(idx), d.r[1] - 3), d.r[1]]);
          else if (d.kind === "hi") setRange([d.r[0], Math.max(c(idx), d.r[0] + 3)]);
          else { const w = d.r[1] - d.r[0]; const l = Math.max(0, Math.min(n - 1 - w, d.r[0] + (idx - d.start))); setRange([l, l + w]); }
        }}
        onPointerUp={() => { drag.current = null; }} onPointerLeave={() => { drag.current = null; }} style={{ touchAction: "none", cursor: "ew-resize" }}>
        <rect x={left} y="0" width={W - left - right} height="46" rx="6" fill="var(--cell)" />
        {dist.bins.map((b, i) => <rect key={i} x={left + i * mbw + mbw * 0.2} y={40 - Math.max(2, (allPct[i] / yMaxAll) * 34)} width={Math.max(2, mbw * 0.6)} height={Math.max(2, (allPct[i] / yMaxAll) * 34)} fill="var(--mute)" opacity=".55" />)}
        {mLabelIdx.map((i) => i > 0 && i < n && <text key={i} x={left + i * mbw} y="30" fontSize="14" fill="var(--text)" opacity=".8" textAnchor="middle">{format(dist.bins[i].from)}</text>)}
        <rect x={left} y="0" width={Math.max(0, lo * mbw)} height="46" fill="#000" opacity=".35" />
        <rect x={left + (hi + 1) * mbw} y="0" width={Math.max(0, (n - hi - 1) * mbw)} height="46" fill="#000" opacity=".35" />
        <rect x={left + lo * mbw} y="0" width={(hi - lo + 1) * mbw} height="46" fill="transparent" stroke="#3b9dff" strokeWidth="1.5" rx="4"
          onPointerDown={(e) => { (e.currentTarget as Element).setPointerCapture?.(e.pointerId); const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect(); drag.current = { kind: "move", start: Math.round(((e.clientX - r.left) / r.width * W - left) / mbw), r: [lo, hi] }; }} />
        <rect x={left + lo * mbw - 4} y="8" width="8" height="30" rx="3" fill="#3b9dff" onPointerDown={(e) => { (e.currentTarget as Element).setPointerCapture?.(e.pointerId); drag.current = { kind: "lo", start: 0, r: [lo, hi] }; e.stopPropagation(); }} />
        <rect x={left + (hi + 1) * mbw - 4} y="8" width="8" height="30" rx="3" fill="#3b9dff" onPointerDown={(e) => { (e.currentTarget as Element).setPointerCapture?.(e.pointerId); drag.current = { kind: "hi", start: 0, r: [lo, hi] }; e.stopPropagation(); }} />
      </svg>
      <div className="sr-only">{format(first.from)} to {format(last.to)}</div>
    </div>
  );
}
