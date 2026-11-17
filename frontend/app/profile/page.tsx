"use client";
import ExportCard from "@/components/ExportCard";
import SyncCard from "@/components/SyncCard";
import Link from "next/link";
import { useEffect, useState } from "react";
import Heatmap from "@/components/Heatmap";
import ProfileCard from "@/components/ProfileCard";
import SolvedCard from "@/components/SolvedCard";
import { Profile, profilePath } from "@/lib/api";
import { useMeta } from "@/lib/meta";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";

const BADGE_ICON: Record<string, string> = { SOLVED: "🎯", HARD: "💎", STREAK: "🔥", ACTIVE: "📅" };

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
  const [error, setError] = useState("");

  useEffect(() => {
    swr<Profile>(profilePath(), (d) => setP(d), () => {}).catch((e) => setError(e.message));
  }, []);

  if (!p) {
    return (
      <>
        {error && <div className="banner err">{error}</div>}
        {!error && <Skeleton lines={10} />}
      </>
    );
  }

  return (
    <>
      <div className="playout">
      <ProfileCard />
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

        <div className="stack"><SyncCard /><ExportCard /></div>

        <section className="card badgescard">
          <div className="bar" style={{ marginBottom: 10 }}>
            <h3 style={{ margin: 0 }}>Badges</h3>
            <b style={{ display: "inline", fontSize: 18 }}>{p.badges.filter((b) => b.earned).length}</b>
            <span className="mute">/ {p.badges.length}</span>
          </div>
          <div className="badges">
            {[...p.badges].sort((a, b) => Number(b.earned) - Number(a.earned)).map((b) => (
              <div key={b.id} className={`badge ${b.earned ? "earned" : "locked"} cat-${b.category}`} title={b.description}>
                <div className="badge-icon" aria-hidden="true">{BADGE_ICON[b.category] ?? "🏅"}</div>
                <div className="badge-title">{b.title}</div>
                {!b.earned && (
                  <div className="badge-progress" aria-label={`${b.progress} of ${b.target}`}>
                    <div style={{ width: `${(b.progress / b.target) * 100}%` }} />
                  </div>
                )}
                <div className="mute" style={{ fontSize: 11 }}>{b.earned ? "Earned" : `${b.progress}/${b.target}`}</div>
              </div>
            ))}
          </div>
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
      </div>
    </>
  );
}
