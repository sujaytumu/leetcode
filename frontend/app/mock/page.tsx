"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { loadAll } from "@/lib/local";
import type { ProblemSummary } from "@/lib/api";
import {
  clearSession, clock, endSession, FORMATS, history, type MockSession, pickProblems, startSession, useMock,
} from "@/lib/mock";

const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

function Result({ s, items }: { s: MockSession; items: ProblemSummary[] }) {
  const rows = s.slugs.map((slug) => {
    const p = items.find((x) => x.slug === slug);
    const solved = p?.status === "SOLVED" && s.baseline[slug] !== "SOLVED";
    return { slug, p, solved, before: s.baseline[slug] === "SOLVED" };
  });
  const got = rows.filter((r) => r.solved).length;
  const used = Math.round(((s.endedAt ?? Date.now()) - s.startedAt) / 1000);
  return (
    <div className="card" style={{ marginBottom: 14 }}>
      <b>{got} of {rows.length} solved</b>
      <div className="mute">{FORMATS.find((f) => f.key === s.format)?.label} · {clock(used)} of {clock(s.durationSec)} used · {new Date(s.startedAt).toLocaleString()}</div>
      <ul className="mockresult">
        {rows.map((r) => (
          <li key={r.slug}>
            <span className={r.solved ? "EASY" : "mute"}>{r.solved ? "✔" : r.before ? "↺" : "✗"}</span>{" "}
            <Link href={`/problems/${r.slug}`}>{r.p ? `${r.p.number ?? r.p.id}. ${r.p.title}` : r.slug}</Link>{" "}
            {r.p && <span className={r.p.difficulty}>{cap(r.p.difficulty)}</span>}
            {r.before && <span className="mute"> (already solved earlier)</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function MockPage() {
  usePageTitle("Mock interview");
  const { session, running, remaining } = useMock();
  const [items, setItems] = useState<ProblemSummary[]>([]);
  const [past, setPast] = useState<MockSession[]>([]);
  const [error, setError] = useState("");

  useEffect(() => { loadAll((d) => setItems(d), () => {}).catch((e) => setError((e as Error).message)); }, []);
  useEffect(() => { setPast(history()); }, [session]);
  const bySlug = useMemo(() => new Set(items.map((p) => p.slug)), [items]);

  return (
    <>
      <h2 style={{ marginTop: 0 }}>Mock interview</h2>
      <p className="mute">Practise under interview conditions: random problems you have not solved yet, a countdown, and no hints, editorial or answers until time is up or you end the session.</p>
      {error && !items.length && <div className="banner err">Could not load problems: {error}</div>}

      {session && running && (
        <div className="card" style={{ marginBottom: 14 }}>
          <b>Session in progress — {clock(remaining)} left</b>
          <ul className="mockresult">
            {session.slugs.map((s, i) => <li key={s}><Link href={`/problems/${s}`}>Problem {i + 1}: {items.find((p) => p.slug === s)?.title ?? s}</Link></li>)}
          </ul>
          <button className="dangerbtn" onClick={() => { if (confirm("End the mock interview now?")) endSession(); }}>End session</button>
        </div>
      )}

      {session && !running && (
        <>
          <h3>Last session</h3>
          <Result s={session} items={items} />
          <button onClick={clearSession}>Dismiss</button>
        </>
      )}

      {!running && (
        <>
          <h3>Start a session</h3>
          <div className="cards">
            {FORMATS.map((f) => (
              <div className="card" key={f.key}>
                <b>{f.label}</b>
                <div className="mute" style={{ margin: "4px 0 10px" }}>{f.blurb}</div>
                <button className="primary" disabled={!items.length}
                  onClick={() => startSession(f, pickProblems(f, items))}>Start · {f.minutes} min</button>
              </div>
            ))}
          </div>
          {!items.length && !error && <p className="mute">Loading problems…</p>}
        </>
      )}

      {past.filter((p) => p.id !== session?.id).length > 0 && (
        <>
          <h3>Earlier sessions</h3>
          {past.filter((p) => p.id !== session?.id).map((p) => <Result key={p.id} s={p} items={items.filter((x) => bySlug.has(x.slug))} />)}
        </>
      )}
    </>
  );
}
