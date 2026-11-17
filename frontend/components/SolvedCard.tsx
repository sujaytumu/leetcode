"use client";
import { MetaOption, Progress } from "@/lib/api";

export const DIFF_COLOR: Record<string, string> = { EASY: "var(--easy)", MEDIUM: "var(--med)", HARD: "var(--hard)" };

/** LeetCode-style solved donut (Easy/Medium/Hard arcs) with per-difficulty boxes. All numbers come from the API. */
export default function SolvedCard({ progress, attempting, difficulties }:
  { progress: Progress; attempting: number; difficulties: MetaOption[] }) {
  const R = 62, C = 2 * Math.PI * R, total = progress.total || 1;
  let offset = 0;
  const arcs = difficulties.map((d) => {
    const len = ((progress.byDifficulty[d.key]?.solved ?? 0) / total) * C;
    const dash = Math.max(0, len - 3);
    const arc = len > 0 ? (
      <circle key={d.key} cx="80" cy="80" r={R} fill="none" stroke={DIFF_COLOR[d.key] ?? "var(--accent)"} strokeWidth="8"
        strokeLinecap="round" strokeDasharray={`${dash} ${C - dash}`} strokeDashoffset={-offset} transform="rotate(-90 80 80)" />
    ) : null;
    offset += len;
    return arc;
  });
  return (
    <section className="card solvedcard">
      <div className="ring">
        <svg viewBox="0 0 160 160" width="160" height="160" role="img" aria-label={`${progress.solved} of ${progress.total} solved`}>
          <circle cx="80" cy="80" r={R} fill="none" stroke="var(--cell)" strokeWidth="8" />
          {arcs}
        </svg>
        <div className="ring-mid">
          <div><b>{progress.solved}</b><span className="mute">/{progress.total}</span></div>
          <div className="mute" style={{ fontSize: 13 }}>✓ Solved</div>
          <div className="mute" style={{ fontSize: 12, marginTop: 6 }}>{attempting} Attempting</div>
        </div>
      </div>
      <div className="diffboxes">
        {difficulties.map((d) => {
          const x = progress.byDifficulty[d.key] ?? { total: 0, solved: 0 };
          return (
            <div key={d.key} className="diffbox">
              <div style={{ color: DIFF_COLOR[d.key], fontWeight: 600, fontSize: 13 }}>{d.label}</div>
              <div style={{ fontWeight: 600 }}>{x.solved}<span className="mute">/{x.total}</span></div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
