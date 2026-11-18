"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, type Page } from "@/lib/api";
import Skeleton from "@/components/Skeleton";

interface Item {
  id: number; slug: string; title: string; verdict: string; language: string;
  passed: number; total: number; runtimeMs: number | null; memoryKb: number | null; createdAt: string;
}
const label = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** Every submission of the caller, following pagination (the server caps a page at 100); stops at 2000 to stay quick. */
async function loadAll(): Promise<Item[]> {
  const out: Item[] = [];
  for (let page = 0; page < 20; page++) {
    const d = await api<Page<Item>>(`/api/submissions?page=${page}&size=100`);
    out.push(...d.items);
    if (page + 1 >= d.totalPages) break;
  }
  return out;
}

function Bars({ rows, color }: { rows: { name: string; value: number; note?: string }[]; color?: string }) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return (
    <div className="hbars">
      {rows.map((r) => (
        <div key={r.name} className="hbar">
          <span className="hb-name">{r.name}</span>
          <span className="hb-track"><span style={{ width: `${(r.value / max) * 100}%`, background: color ?? "var(--accent)" }} /></span>
          <span className="hb-val">{r.value}{r.note ? ` ${r.note}` : ""}</span>
        </div>
      ))}
    </div>
  );
}

export default function StatsPage() {
  const [items, setItems] = useState<Item[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { loadAll().then(setItems).catch((e: Error) => setError(e.message)); }, []);

  const s = useMemo(() => {
    if (!items) return null;
    const total = items.length, ac = items.filter((i) => i.verdict === "ACCEPTED").length;
    const verdicts = new Map<string, number>(), langs = new Map<string, { n: number; ac: number }>();
    const weekday = new Array<number>(7).fill(0), hour = new Array<number>(24).fill(0);
    const byProblem = new Map<string, Item[]>();
    for (const i of items) {
      verdicts.set(i.verdict, (verdicts.get(i.verdict) ?? 0) + 1);
      const l = langs.get(i.language) ?? { n: 0, ac: 0 };
      l.n++; if (i.verdict === "ACCEPTED") l.ac++;
      langs.set(i.language, l);
      const d = new Date(i.createdAt);
      weekday[d.getDay()]++; hour[d.getHours()]++;
      (byProblem.get(i.slug || i.title) ?? byProblem.set(i.slug || i.title, []).get(i.slug || i.title)!).push(i);
    }
    // Per problem: attempts (oldest first) until the first accepted one.
    let solved = 0, firstTry = 0, attemptsSum = 0;
    const struggles: { title: string; slug: string; tries: number; solved: boolean }[] = [];
    for (const list of byProblem.values()) {
      const asc = [...list].sort((a, b) => a.id - b.id);
      const k = asc.findIndex((x) => x.verdict === "ACCEPTED");
      if (k >= 0) { solved++; attemptsSum += k + 1; if (k === 0) firstTry++; }
      struggles.push({ title: asc[0].title, slug: asc[0].slug, tries: k >= 0 ? k + 1 : asc.length, solved: k >= 0 });
    }
    struggles.sort((a, b) => b.tries - a.tries);
    const mostActiveHour = hour.indexOf(Math.max(...hour));
    return { total, ac, verdicts, langs, weekday, hour, solved, firstTry, attemptsSum, struggles: struggles.slice(0, 5),
      problems: byProblem.size, mostActiveHour };
  }, [items]);

  if (error) return <div className="banner err">{error}</div>;
  if (!s) return <Skeleton lines={8} />;
  if (s.total === 0) return <p className="mute">No submissions yet. Submit a solution and your stats show up here.</p>;

  const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 100)}%` : "–");
  return (
    <>
      <div className="bar" style={{ marginBottom: 10 }}>
        <h2 style={{ margin: 0 }}>My stats</h2><span className="grow" />
        <Link href="/submissions">All submissions</Link> · <Link href="/profile">← Profile</Link>
      </div>
      <div className="cards">
        <div className="card"><span className="mute">Submissions</span><b>{s.total}</b></div>
        <div className="card"><span className="mute">Acceptance rate</span><b>{pct(s.ac, s.total)}</b></div>
        <div className="card"><span className="mute">Problems solved</span><b>{s.solved}<span className="mute" style={{ fontSize: 14 }}> / {s.problems} tried</span></b></div>
        <div className="card"><span className="mute">First-try solves</span><b>{pct(s.firstTry, s.solved)}</b></div>
        <div className="card"><span className="mute">Avg attempts to solve</span><b>{s.solved ? (s.attemptsSum / s.solved).toFixed(1) : "–"}</b></div>
      </div>
      <div className="statgrid">
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>Verdicts</h3>
          <Bars rows={[...s.verdicts].sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ name: label(k), value: v, note: `(${pct(v, s.total)})` }))} /></section>
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>Languages</h3>
          <Bars rows={[...s.langs].sort((a, b) => b[1].n - a[1].n).map(([k, v]) => ({ name: k, value: v.n, note: `(${pct(v.ac, v.n)} AC)` }))} /></section>
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>By weekday</h3>
          <Bars rows={s.weekday.map((v, i) => ({ name: DAYS[i], value: v }))} color="var(--easy)" /></section>
        <section className="card"><h3 style={{ margin: "0 0 4px" }}>By hour of day</h3>
          <p className="mute" style={{ fontSize: 12, margin: "0 0 8px" }}>You submit most around {String(s.mostActiveHour).padStart(2, "0")}:00.</p>
          <div className="hourbars" aria-label="Submissions by hour">
            {s.hour.map((v, h) => <span key={h} title={`${String(h).padStart(2, "0")}:00 · ${v}`} style={{ height: `${(v / Math.max(1, ...s.hour)) * 100}%` }} />)}
          </div></section>
        <section className="card" style={{ gridColumn: "1 / -1" }}><h3 style={{ margin: "0 0 8px" }}>Problems that took the most attempts</h3>
          {s.struggles.map((p) => (
            <div key={p.slug || p.title} className="recentrow" style={{ cursor: "default" }}>
              {p.slug ? <Link href={`/problems/${p.slug}`}>{p.title}</Link> : <span>{p.title}</span>}
              <span className="grow" />
              <span className="mute" style={{ fontSize: 13 }}>{p.tries} attempt{p.tries === 1 ? "" : "s"} · {p.solved ? "solved" : "unsolved"}</span>
            </div>
          ))}</section>
      </div>
    </>
  );
}
