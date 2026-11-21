"use client";
import { MetaOption, Progress } from "@/lib/api";

export const DIFF_COLOR: Record<string, string> = { EASY: "var(--easy)", MEDIUM: "var(--med)", HARD: "var(--hard)" };

/** Easy is teal in LeetCode's solved gauge (the site-wide green is used for the check mark). */
const GAUGE: Record<string, string> = { EASY: "#00b8a3", MEDIUM: "var(--med)", HARD: "var(--hard)" };
const START = 210, SPAN = 300, GAP = 7; // degrees clockwise from 12 o'clock; the gauge is open at the bottom

const polar = (r: number, deg: number): [number, number] => {
  const a = (deg * Math.PI) / 180;
  return [80 + r * Math.sin(a), 80 - r * Math.cos(a)];
};
const arcPath = (r: number, a0: number, a1: number) => {
  const [x0, y0] = polar(r, a0), [x1, y1] = polar(r, a1);
  return `M${x0.toFixed(2)},${y0.toFixed(2)} A${r},${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(2)},${y1.toFixed(2)}`;
};

/** LeetCode-style solved gauge: one segment per difficulty (sized by its share of all problems), filled as you solve. */
export default function SolvedCard({ progress, attempting, difficulties }:
  { progress: Progress; attempting: number; difficulties: MetaOption[] }) {
  const R = 68;
  const totalAll = difficulties.reduce((n, d) => n + (progress.byDifficulty[d.key]?.total ?? 0), 0) || 1;
  const usable = SPAN - GAP * Math.max(0, difficulties.length - 1);
  let cursor = START;
  const segs = difficulties.map((d) => {
    const x = progress.byDifficulty[d.key] ?? { total: 0, solved: 0 };
    const len = (x.total / totalAll) * usable;
    const a0 = cursor, a1 = cursor + len;
    cursor = a1 + GAP;
    const color = GAUGE[d.key] ?? "var(--accent)";
    const fill = x.total ? Math.min(1, x.solved / x.total) : 0;
    return (
      <g key={d.key}>
        {len > 0 && <path d={arcPath(R, a0, a1)} fill="none" stroke={color} strokeOpacity="0.25" strokeWidth="3.5" strokeLinecap="round" />}
        {len > 0 && fill > 0 && <path d={arcPath(R, a0, a0 + Math.max(1, len * fill))} fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" />}
      </g>
    );
  });
  return (
    <section className="card solvedcard">
      <div className="ring">
        <svg viewBox="0 0 160 160" width="160" height="160" role="img" aria-label={`${progress.solved} of ${progress.total} solved`}>
          {segs}
        </svg>
        <div className="ring-mid">
          <div className="ring-num"><b>{progress.solved}</b><span className="mute">/{progress.total}</span></div>
          <div className="ring-solved">✓ Solved</div>
        </div>
        <div className="ring-attempt mute">{attempting} Attempting</div>
      </div>
      <div className="diffboxes">
        {difficulties.map((d) => {
          const x = progress.byDifficulty[d.key] ?? { total: 0, solved: 0 };
          return (
            <div key={d.key} className="diffbox">
              <div style={{ color: GAUGE[d.key], fontWeight: 600, fontSize: 14 }}>{d.label}</div>
              <div style={{ fontWeight: 600 }}>{x.solved}<span className="mute">/{x.total}</span></div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
