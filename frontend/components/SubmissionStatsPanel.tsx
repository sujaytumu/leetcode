"use client";
import { useEffect, useState } from "react";
import { api, type Distribution, type SubmissionStats } from "@/lib/api";
import StatsChart from "./StatsChart";

export const fmtMs = (v: number) => `${v} ms`;
export const fmtMem = (kb: number) => `${(kb / 1024).toFixed(1)} MB`;

function Block({ title, dist, format, hint }: { title: string; dist: Distribution; format: (v: number) => string; hint: string }) {
  return (
    <div className="statblock">
      <div className="stathead"><span>{title}</span></div>
      <div className="statvalue"><b>{format(dist.value)}</b>
        {dist.beatsPercent != null
          ? <span className="beats">Beats <b>{dist.beatsPercent}%</b> of users</span>
          : <span className="mute">You are the only one with an accepted solution here so far</span>}
      </div>
      <StatsChart dist={dist} format={format} label={title} />
      <div className="mute stathint">{hint}</div>
    </div>
  );
}

/** Runtime and memory of an accepted submission compared with everyone else's accepted submissions in the same language. */
export default function SubmissionStatsPanel({ id }: { id: number }) {
  const [stats, setStats] = useState<SubmissionStats | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    setStats(null); setError("");
    api<SubmissionStats>(`/api/submissions/${id}/stats`, {}, 30000)
      .then((s) => alive && setStats(s)).catch((e) => alive && setError((e as Error).message));
    return () => { alive = false; };
  }, [id]);
  if (error) return <div className="mute">Could not load the comparison charts ({error}).</div>;
  if (!stats) return <div className="mute">Loading runtime and memory comparison…</div>;
  return (
    <div className="statsgrid">
      {stats.runtime && <Block title="Runtime" dist={stats.runtime} format={fmtMs}
        hint={`Compared with each of the ${stats.sampleSize} user${stats.sampleSize === 1 ? "" : "s"} who solved this in ${stats.language} (best submission per user). Slowest test case, as measured by the judge.`} />}
      {stats.memory
        ? <Block title="Memory" dist={stats.memory} format={fmtMem} hint="Peak memory over all test cases, as measured by the judge." />
        : <div className="mute">Memory was not reported by the judge for this submission.</div>}
    </div>
  );
}
