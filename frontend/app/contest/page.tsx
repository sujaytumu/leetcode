"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type Difficulty } from "@/lib/api";
import Skeleton from "@/components/Skeleton";

interface ContestProblem { slug: string; title: string; difficulty: Difficulty; points: number }
interface ContestView { id: number; title: string; start: string; end: string; state: "UPCOMING" | "RUNNING" | "FINISHED"; problems: ContestProblem[] | null }
interface Row { rank: number; name: string; score: number; finishSeconds: number; solved: boolean[]; you: boolean }
interface Standings { contest: ContestView; participants: number; rows: Row[]; me: Row | null }
interface Overview { now: string; current: ContestView; past: ContestView[] }

const pad = (n: number) => String(n).padStart(2, "0");
const clock = (secs: number) => {
  const s = Math.max(0, Math.floor(secs));
  const d = Math.floor(s / 86400);
  const rest = `${pad(Math.floor((s % 86400) / 3600))}:${pad(Math.floor((s % 3600) / 60))}:${pad(s % 60)}`;
  return d > 0 ? `${d}d ${rest}` : rest;
};
const finish = (secs: number) => `${Math.floor(secs / 3600)}:${pad(Math.floor((secs % 3600) / 60))}:${pad(secs % 60)}`;
const when = (iso: string) => new Date(iso).toLocaleString(undefined, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

export default function ContestPage() {
  usePageTitle("Contests");
  const [overview, setOverview] = useState<Overview | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [standings, setStandings] = useState<Standings | null>(null);
  const [error, setError] = useState("");
  const [now, setNow] = useState(() => Date.now());
  const [skew, setSkew] = useState(0); // server time minus browser time, so the countdown follows the server's clock

  useEffect(() => {
    api<Overview>("/api/contests")
      .then((o) => { setOverview(o); setSkew(new Date(o.now).getTime() - Date.now()); setSelected((s) => s ?? o.current.id); })
      .catch((e: Error) => setError(e.message));
  }, []);
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(t); }, []);

  const loadStandings = useCallback((id: number) => {
    api<Standings>(`/api/contests/${id}`).then((s) => { setStandings(s); setError(""); }).catch((e: Error) => setError(e.message));
  }, []);
  useEffect(() => {
    if (selected == null) return;
    setStandings(null);
    loadStandings(selected);
  }, [selected, loadStandings]);
  // keep a running contest fresh, and refetch when its start time passes so the problems appear
  const state = standings?.contest.state;
  useEffect(() => {
    if (selected == null || state === "FINISHED") return;
    const t = setInterval(() => loadStandings(selected), state === "RUNNING" ? 30000 : 15000);
    return () => clearInterval(t);
  }, [selected, state, loadStandings]);

  const c = standings?.contest;
  const tabs = overview ? [overview.current, ...overview.past] : [];
  const serverNow = now + skew;
  const toStart = c ? (new Date(c.start).getTime() - serverNow) / 1000 : 0;
  const toEnd = c ? (new Date(c.end).getTime() - serverNow) / 1000 : 0;
  const mine = standings?.me?.solved ?? [];

  return (
    <>
      <h2 style={{ marginBottom: 4 }}>Contest</h2>
      <p className="mute" style={{ marginTop: 0 }}>
        A new contest runs every Sunday for 90 minutes. Solve the four problems on their normal pages; every accepted
        submission made during the window counts. Points are 3, 4, 5 and 6, plus a 5 minute penalty for each wrong answer
        before you pass a problem.
      </p>
      {error && <div className="banner err">{error}</div>}
      {!overview && !error && <Skeleton />}
      {overview && (
        <div className="chips">
          {tabs.map((t) => (
            <button key={t.id} className={selected === t.id ? "on" : ""} onClick={() => setSelected(t.id)}>
              {t.title}{t.state === "RUNNING" ? " · live" : t.state === "UPCOMING" ? " · next" : ""}
            </button>
          ))}
        </div>
      )}
      {overview && !standings && !error && <Skeleton />}
      {c && standings && (
        <>
          <div className="card contest-head">
            <div>
              <b style={{ fontSize: 18 }}>{c.title}</b>{" "}
              <span className={`pill ${c.state === "RUNNING" ? "EASY" : c.state === "UPCOMING" ? "MEDIUM" : ""}`}>{c.state.toLowerCase()}</span>
              <div className="mute">{when(c.start)} – {new Date(c.end).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}</div>
            </div>
            <span className="grow" />
            {c.state === "UPCOMING" && <div className="countdown"><div className="mute">Starts in</div><b>{clock(toStart)}</b></div>}
            {c.state === "RUNNING" && <div className="countdown"><div className="mute">Ends in</div><b>{clock(toEnd)}</b></div>}
            {c.state === "FINISHED" && <div className="countdown"><div className="mute">Participants</div><b>{standings.participants}</b></div>}
          </div>

          {c.problems ? (
            <table style={{ marginTop: 12 }}>
              <thead><tr><th style={{ width: 40 }}></th><th>Problem</th><th>Difficulty</th><th className="th-num">Points</th></tr></thead>
              <tbody>
                {c.problems.map((p, i) => (
                  <tr key={p.slug}>
                    <td className="EASY">{mine[i] ? "✔" : ""}</td>
                    <td><Link href={`/problems/${p.slug}`}>Q{i + 1}. {p.title}</Link></td>
                    <td className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</td>
                    <td className="th-num">{p.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="mute" style={{ marginTop: 12 }}>The four problems are revealed when the contest starts.</p>
          )}

          {c.problems && (
            <>
              <h3 style={{ marginBottom: 6 }}>Standings</h3>
              {standings.me && !standings.rows.some((r) => r.you) && (
                <p className="mute">You are ranked #{standings.me.rank} with {standings.me.score} points.</p>
              )}
              <div className="tscroll"><table>
                <thead><tr><th className="th-num" style={{ width: 56 }}>Rank</th><th>User</th><th className="th-num">Score</th>
                  <th className="th-num">Finish time</th>{c.problems.map((_, i) => <th key={i} className="th-num">Q{i + 1}</th>)}</tr></thead>
                <tbody>
                  {standings.rows.map((r) => (
                    <tr key={r.rank} className={r.you ? "me-row" : ""}>
                      <td className="th-num">{r.rank}</td>
                      <td><b>{r.name}</b>{r.you && <span className="pill MEDIUM" style={{ marginLeft: 6 }}>you</span>}</td>
                      <td className="th-num"><b>{r.score}</b></td>
                      <td className="th-num">{finish(r.finishSeconds)}</td>
                      {r.solved.map((s, i) => <td key={i} className={`th-num ${s ? "EASY" : "mute"}`}>{s ? "✔" : "–"}</td>)}
                    </tr>
                  ))}
                  {standings.rows.length === 0 && (
                    <tr><td colSpan={4 + c.problems.length} className="mute">
                      {c.state === "RUNNING" ? "Nobody has scored yet. Be the first." : "Nobody scored in this contest."}
                    </td></tr>
                  )}
                </tbody>
              </table></div>
            </>
          )}
        </>
      )}
    </>
  );
}
