"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type Submission } from "@/lib/api";

interface P { slug: string; title: string; points: number }
const LENGTH = 90 * 60;
const pad = (n: number) => String(n).padStart(2, "0");
const clock = (s: number) => `${Math.floor(s / 3600)}:${pad(Math.floor((s % 3600) / 60))}:${pad(s % 60)}`;
const keyOf = (id: number) => `lc-virtual-${id}`;

/** A private, timed re-run of a finished contest: 90 minutes, same scoring (5 minute penalty per wrong answer). Kept on this device. */
export default function VirtualContest({ contestId, problems }: { contestId: number; problems: P[] }) {
  const [start, setStart] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [subs, setSubs] = useState<Record<string, Submission[]>>({});

  useEffect(() => {
    try { const v = localStorage.getItem(keyOf(contestId)); setStart(v ? Number(v) : null); } catch { setStart(null); }
  }, [contestId]);
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(t); }, []);

  const load = useCallback(() => {
    for (const p of problems) {
      api<Submission[]>(`/api/problems/${p.slug}/submissions`).then((h) => setSubs((s) => ({ ...s, [p.slug]: h }))).catch(() => {});
    }
  }, [problems]);
  const elapsed = start ? Math.floor((now - start) / 1000) : 0;
  const over = start != null && elapsed >= LENGTH;
  useEffect(() => {
    if (!start || over) return;
    load();
    const t = setInterval(load, 20000);
    return () => clearInterval(t);
  }, [start, over, load]);
  useEffect(() => { if (over) load(); }, [over, load]);

  function begin() {
    const t = Date.now();
    try { localStorage.setItem(keyOf(contestId), String(t)); } catch { /* storage blocked */ }
    setStart(t); setSubs({});
  }
  function reset() {
    try { localStorage.removeItem(keyOf(contestId)); } catch { /* storage blocked */ }
    setStart(null); setSubs({});
  }

  if (!start) {
    return (
      <div className="card contest-me" style={{ alignItems: "center" }}>
        <div><b style={{ fontSize: 16 }}>Virtual contest</b><div className="mute">Re-run this contest on your own: 90 minutes, same points and penalties. Your normal submissions count while the clock runs.</div></div>
        <span className="grow" />
        <button className="primary" onClick={begin}>Start virtual contest</button>
      </div>
    );
  }
  const begun = start;
  const rows = problems.map((p) => {
    const inWindow = (subs[p.slug] ?? [])
      .filter((s) => { const t = new Date(s.createdAt).getTime(); return t >= begun && t <= begun + LENGTH * 1000; })
      .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
    const ok = inWindow.find((s) => s.verdict === "ACCEPTED");
    if (!ok) return { p, solved: false, at: 0, wrong: 0 };
    const wrong = inWindow.filter((s) => s.id !== ok.id && s.verdict !== "ACCEPTED" && s.verdict !== "COMPILE_ERROR" && s.verdict !== "INTERNAL_ERROR"
      && new Date(s.createdAt).getTime() < new Date(ok.createdAt).getTime()).length;
    return { p, solved: true, at: Math.floor((new Date(ok.createdAt).getTime() - begun) / 1000), wrong };
  });
  const score = rows.reduce((a, r) => a + (r.solved ? r.p.points : 0), 0);
  const finishSecs = rows.reduce((m, r) => (r.solved ? Math.max(m, r.at + r.wrong * 300) : m), 0);
  return (
    <div className="card contest-me" style={{ display: "block" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <b style={{ fontSize: 16 }}>Virtual contest</b>
        <span className={over ? "mute" : "ok-tick"}>{over ? "Finished" : `Time left ${clock(LENGTH - elapsed)}`}</span>
        <span className="grow" />
        <span>Score <b>{score}</b></span>
        <span>Finish <b>{score ? clock(finishSecs) : "–"}</b></span>
        <button onClick={reset}>{over ? "Reset" : "Abandon"}</button>
      </div>
      <div style={{ display: "grid", gap: 6, marginTop: 10 }}>
        {rows.map((r, i) => (
          <div key={r.p.slug} style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <span className={r.solved ? "ok-tick" : "mute"} style={{ width: 18 }}>{r.solved ? "✔" : "–"}</span>
            <Link href={`/problems/${r.p.slug}`}>Q{i + 1}. {r.p.title}</Link>
            <span className="mute">({r.p.points})</span>
            <span className="grow" />
            {r.solved && <span className="mute">{clock(r.at)}{r.wrong ? ` · +${r.wrong * 5}m` : ""}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
