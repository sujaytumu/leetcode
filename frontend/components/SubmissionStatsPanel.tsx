"use client";
import { useEffect, useState } from "react";
import { api, type Distribution, type SubmissionStats } from "@/lib/api";
import StatsChart from "./StatsChart";

export const fmtMs = (v: number) => `${v} ms`;
export const fmtMem = (kb: number) => `${(kb / 1024).toFixed(1)} MB`;
const axisMs = (v: number) => `${v}ms`;
const axisMem = (kb: number) => `${Math.round(kb / 1024)}MB`;

function Metric({ icon, name, dist, unit, active, onPick }: { icon: string; name: string; dist: Distribution; unit: string; active: boolean; onPick: () => void }) {
  return (
    <button type="button" className={`lcmetric${active ? " on" : ""}`} onClick={onPick} aria-pressed={active}>
      <span className="lcmetric-name"><span aria-hidden="true">{icon}</span> {name}</span>
      <span className="lcmetric-row">
        <b className="lcmetric-val">{unit}</b>
        {dist.beatsPercent != null
          ? <span className="lcmetric-beats"><span className="mute">Beats</span> <b>{dist.beatsPercent}%</b>{dist.beatsPercent >= 50 ? " 👋" : ""}</span>
          : <span className="mute lcmetric-beats">Only accepted solution so far</span>}
      </span>
    </button>
  );
}

/** Runtime and memory of an accepted submission compared with everyone else's accepted submissions in the same language (LeetCode layout). */
export default function SubmissionStatsPanel({ id }: { id: number }) {
  const [stats, setStats] = useState<SubmissionStats | null>(null);
  const [error, setError] = useState("");
  const [metric, setMetric] = useState<"runtime" | "memory">("runtime");
  useEffect(() => {
    let alive = true;
    setStats(null); setError("");
    api<SubmissionStats>(`/api/submissions/${id}/stats`, {}, 30000)
      .then((s) => alive && setStats(s)).catch((e) => alive && setError((e as Error).message));
    return () => { alive = false; };
  }, [id]);
  if (error) return <div className="mute">Could not load the comparison charts ({error}).</div>;
  if (!stats) return <div className="mute">Loading runtime and memory comparison…</div>;
  const active = metric === "memory" && stats.memory ? "memory" : "runtime";
  const d = active === "memory" ? stats.memory! : stats.runtime;
  return (
    <div className="lcstats">
      {stats.runtime && <Metric icon="◷" name="Runtime" dist={stats.runtime} unit={`${stats.runtime.value} ms`} active={active === "runtime"} onPick={() => setMetric("runtime")} />}
      {stats.memory
        ? <Metric icon="▣" name="Memory" dist={stats.memory} unit={`${(stats.memory.value / 1024).toFixed(2)} MB`} active={active === "memory"} onPick={() => setMetric("memory")} />
        : <div className="mute">Memory was not reported by the judge for this submission.</div>}
      {d && <StatsChart dist={d} format={active === "memory" ? axisMem : axisMs} label={active === "memory" ? "Memory" : "Runtime"} noun={active === "memory" ? "memory" : "runtime"} />}
      <div className="mute stathint">Compared with each of the {stats.sampleSize} user{stats.sampleSize === 1 ? "" : "s"} who solved this in {stats.language} (best submission per user), as measured by the judge.</div>
    </div>
  );
}
