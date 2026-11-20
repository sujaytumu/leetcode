"use client";
import Link from "next/link";
import { ReactNode, useState } from "react";
import Heatmap from "@/components/Heatmap";
import SkillsCard from "@/components/SkillsCard";
import CommunityStats from "@/components/CommunityStats";
import ContestRating from "@/components/ContestRating";
import SolvedCard from "@/components/SolvedCard";
import ProfileTabs from "@/components/ProfileTabs";
import { Profile } from "@/lib/api";
import { useMeta } from "@/lib/meta";

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

/**
 * The body of a LeetCode-style profile, shared by your own page and public pages: header card in the left column
 * (passed in), then community stats, languages and skills; rating, solved ring, activity, badges and recent
 * accepted on the right. {@code extras} is for owner-only cards (sync, export).
 */
export default function ProfileLayout({ p, header, ratingPath = "/api/profile/rating", own = true, extras }:
  { p: Profile; header: ReactNode; ratingPath?: string; own?: boolean; extras?: ReactNode }) {
  const meta = useMeta();
  const [year, setYear] = useState<number | "current">("current");
  const years = [...new Set(p.calendar.map((c) => Number(c.date.slice(0, 4))))].sort((a, b) => b - a);
  return (
    <>
      <div className="playout">
      <div className="stack pleft">
        {header}
        {p.community && <CommunityStats stats={p.community} />}
        <section className="card langskills">
          <h3 className="sect-h">Languages</h3>
          {p.languages.length === 0 && <p className="mute">—</p>}
          {p.languages.map((l) => (
            <div key={l.language} className="langrow">
              <span className="skillchip">{l.language}</span>
              <span className="mute"><b>{l.solved}</b> problems solved</span>
            </div>
          ))}
          <hr className="sect-hr" />
          <h3 className="sect-h">Skills</h3>
          <SkillsCard skills={p.skills} />
        </section>
      </div>
      <div className="pgrid">
        <div className="stack ratingcol"><ContestRating path={ratingPath} /></div>
        {meta && <SolvedCard progress={p.progress} attempting={p.attempting} difficulties={meta.difficulties} />}

        <section className="card badgescard">
          {(() => {
            const earned = p.badges.filter((b) => b.earned);
            const recent = earned[earned.length - 1];
            return (
              <>
                <div className="bd-top">
                  <div>
                    <div className="bd-label">Badges</div>
                    <div className="bd-count">{earned.length}</div>
                  </div>
                  <div className="bd-medals" aria-hidden="true">
                    {[...earned.slice(-3).reverse(), ...p.badges.filter((b) => !b.earned)].slice(0, 3).map((b) => (
                      <span key={b.id} className={`bd-hex cat-${b.category}${b.earned ? "" : " locked"}`} title={b.earned ? b.title : `${b.title} (locked)`}>{BADGE_ICON[b.category] ?? "🏅"}</span>
                    ))}
                  </div>
                </div>
                <div className="bd-recent">
                  <span className="mute">Most Recent Badge</span>
                  <b>{recent ? recent.title : "None yet"}</b>
                </div>
              </>
            );
          })()}
          <details className="bd-all">
            <summary>All badges ({p.badges.filter((b) => b.earned).length} / {p.badges.length})</summary>
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
          </details>
        </section>

        <section className="card activitycard">
          <div className="act-title"><b>{p.submissionsPastYear}</b> <span>submissions in the past one year</span><span className="act-info" title="Counts every accepted or attempted submission in the last 365 days. Darker squares mean more submissions that day." aria-label="About this calendar">i</span></div>
          <div className="act-stats">
            <span className="mute">Total active{" "}<br />days: <b>{p.activeDays}</b></span>
            <span className="mute">Max{" "}<br />streak: <b>{p.maxStreak}</b></span>
            <span className="grow" />
            <select className="act-year" aria-label="Calendar range" value={String(year)}
              onChange={(e) => setYear(e.target.value === "current" ? "current" : Number(e.target.value))}>
              <option value="current">Current</option>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <Heatmap calendar={p.calendar} year={year === "current" ? undefined : year} />
        </section>



        <div className="recentcard"><ProfileTabs p={p} own={own} /></div>

        {extras && <div className="pextras">{extras}</div>}

      </div>
      </div>
    </>
  );
}
