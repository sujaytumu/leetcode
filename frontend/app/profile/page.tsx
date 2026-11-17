"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import Heatmap from "@/components/Heatmap";
import SolvedCard from "@/components/SolvedCard";
import { Profile, profilePath } from "@/lib/api";
import { useMeta } from "@/lib/meta";
import { swr } from "@/lib/local";

function ago(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  const unit = (n: number, name: string) => (n === 1 ? `a ${name} ago` : `${n} ${name}s ago`);
  if (s < 60) return "just now";
  if (s < 3600) return unit(Math.floor(s / 60), "minute");
  if (s < 86400) return unit(Math.floor(s / 3600), "hour");
  if (s < 86400 * 30) return unit(Math.floor(s / 86400), "day");
  if (s < 86400 * 365) return unit(Math.floor(s / (86400 * 30)), "month");
  return unit(Math.floor(s / (86400 * 365)), "year");
}

export default function ProfilePage() {
  const meta = useMeta();
  const [p, setP] = useState<Profile | null>(null);
  const [saved, setSaved] = useState(false);
  const [waking, setWaking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    swr<Profile>(profilePath(), (d, fromCache) => { setP(d); setSaved(fromCache); }, () => setWaking(true))
      .then(() => setWaking(false))
      .catch((e) => { setError(e.message); setWaking(false); });
  }, []);

  if (!p) {
    return (
      <>
        {waking && <div className="banner warn">Waking up the server (free hosting sleeps when idle). Retrying automatically…</div>}
        {error && <div className="banner err">{error}</div>}
        {!waking && !error && <p className="mute">Loading…</p>}
      </>
    );
  }

  return (
    <>
      {saved && <div className="banner warn">Showing a saved copy{waking ? " while the server wakes up — refreshing automatically…" : "."}</div>}
      <div className="pgrid">
        {meta && <SolvedCard progress={p.progress} attempting={p.attempting} difficulties={meta.difficulties} />}

        <section className="card activitycard">
          <div className="bar" style={{ flexWrap: "wrap", gap: 16, marginBottom: 8 }}>
            <span><b style={{ display: "inline", fontSize: 18 }}>{p.submissionsPastYear}</b> <span className="mute">submissions in the past year</span></span>
            <span className="grow" />
            <span className="mute" style={{ fontSize: 13 }}>Active days: <b style={{ display: "inline", fontSize: 13 }}>{p.activeDays}</b></span>
            <span className="mute" style={{ fontSize: 13 }}>Max streak: <b style={{ display: "inline", fontSize: 13 }}>{p.maxStreak}</b></span>
            <span className="mute" style={{ fontSize: 13 }}>Current: <b style={{ display: "inline", fontSize: 13 }}>{p.currentStreak}</b></span>
          </div>
          <Heatmap calendar={p.calendar} />
        </section>

        <section className="card recentcard">
          <h3 style={{ margin: "0 0 8px" }}>Recent AC</h3>
          {p.recentAccepted.length === 0 && <p className="mute">No accepted submissions yet. Solve a problem and it shows up here.</p>}
          {p.recentAccepted.map((r, i) => (
            <Link key={`${r.slug}-${i}`} href={`/problems/${r.slug}`} className="recentrow">
              <span>{r.title}</span>
              <span className={r.difficulty} style={{ fontSize: 12 }}>{r.difficulty[0] + r.difficulty.slice(1).toLowerCase()}</span>
              <span className="grow" />
              <span className="mute" style={{ fontSize: 13 }}>{ago(r.at)}</span>
            </Link>
          ))}
        </section>

        <aside className="card sidecard">
          <h3 style={{ margin: "0 0 8px" }}>Languages</h3>
          {p.languages.length === 0 && <p className="mute">—</p>}
          {p.languages.map((l) => (
            <div key={l.language} className="bar" style={{ padding: "3px 0" }}>
              <span className="tag">{l.language}</span><span className="grow" />
              <span className="mute" style={{ fontSize: 13 }}><b style={{ display: "inline", fontSize: 13 }}>{l.solved}</b> problems solved</span>
            </div>
          ))}
          <h3 style={{ margin: "16px 0 8px" }}>Skills</h3>
          {p.skills.length === 0 && <p className="mute">Topics you solve appear here.</p>}
          <div>{p.skills.map((s) => <span key={s.tag} className="tag skill">{s.tag} <span className="mute">×{s.solved}</span></span>)}</div>
        </aside>
      </div>
    </>
  );
}
