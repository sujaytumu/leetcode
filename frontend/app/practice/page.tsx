"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import Skeleton from "@/components/Skeleton";
import { Difficulty, ProblemSummary, tagLabel } from "@/lib/api";
import { loadAll } from "@/lib/local";

const KEY = "lc-practice";
const DIFFS: Difficulty[] = ["EASY", "MEDIUM", "HARD"];

function shuffle<T>(a: T[]): T[] {
  const x = [...a];
  for (let i = x.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [x[i], x[j]] = [x[j], x[i]]; }
  return x;
}

/** Build a custom practice set: pick topics, difficulties and size; get a random set of problems you have not solved. */
export default function PracticePage() {
  usePageTitle("Practice session");
  const [all, setAll] = useState<ProblemSummary[] | null>(null);
  const [error, setError] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [diffs, setDiffs] = useState<Difficulty[]>(["EASY", "MEDIUM"]);
  const [count, setCount] = useState(5);
  const [unsolvedOnly, setUnsolvedOnly] = useState(true);
  const [session, setSession] = useState<string[]>([]);

  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("tag");
    if (t) setTags([t]);
    try { const s = JSON.parse(localStorage.getItem(KEY) ?? "[]"); if (Array.isArray(s)) setSession(s.filter((x) => typeof x === "string")); } catch { /* corrupt */ }
    loadAll((items) => setAll(items), () => {}).catch((e: Error) => setError(e.message));
  }, []);

  const allTags = useMemo(() => {
    const n = new Map<string, number>();
    (all ?? []).forEach((p) => p.tags.forEach((t) => n.set(t, (n.get(t) ?? 0) + 1)));
    return [...n].sort((a, b) => b[1] - a[1]).map(([t]) => t);
  }, [all]);

  const pool = useMemo(() => (all ?? []).filter((p) =>
    (!tags.length || p.tags.some((t) => tags.includes(t))) && diffs.includes(p.difficulty) && (!unsolvedOnly || p.status !== "SOLVED")),
  [all, tags, diffs, unsolvedOnly]);

  const toggle = <T,>(list: T[], v: T) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v]);
  const generate = () => {
    const next = shuffle(pool).slice(0, count).map((p) => p.slug);
    setSession(next);
    try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* storage blocked */ }
  };

  const bySlug = useMemo(() => new Map((all ?? []).map((p) => [p.slug, p])), [all]);
  const picked = session.map((s) => bySlug.get(s)).filter((p): p is ProblemSummary => !!p);
  const solved = picked.filter((p) => p.status === "SOLVED").length;

  if (error) return <div className="banner err">{error}</div>;
  if (!all) return <Skeleton lines={8} />;
  return (
    <>
      <h2 style={{ marginTop: 0 }}>Practice session</h2>
      <section className="card" style={{ marginBottom: 16 }}>
        <div className="iolabel">Topics <span className="mute">(none selected = any)</span></div>
        <div className="chips">
          {allTags.map((t) => (
            <button key={t} type="button" className={`chip${tags.includes(t) ? " on" : ""}`} onClick={() => setTags(toggle(tags, t))}>{tagLabel(t)}</button>
          ))}
        </div>
        <div className="bar" style={{ flexWrap: "wrap", marginTop: 12, gap: 12 }}>
          {DIFFS.map((d) => (
            <label key={d} className={d}><input type="checkbox" checked={diffs.includes(d)} onChange={() => setDiffs(toggle(diffs, d))} /> {d[0] + d.slice(1).toLowerCase()}</label>
          ))}
          <label>Size <select value={count} onChange={(e) => setCount(Number(e.target.value))}>{[3, 5, 8, 10].map((n) => <option key={n} value={n}>{n}</option>)}</select></label>
          <label><input type="checkbox" checked={unsolvedOnly} onChange={(e) => setUnsolvedOnly(e.target.checked)} /> Unsolved only</label>
          <span className="grow" />
          <span className="mute">{pool.length} match</span>
          <button className="primary" disabled={!pool.length || !diffs.length} onClick={generate}>{session.length ? "New session" : "Start session"}</button>
        </div>
      </section>
      {picked.length > 0 && (
        <section>
          <div className="bar" style={{ marginBottom: 8 }}>
            <h3 style={{ margin: 0 }}>Your session</h3><span className="grow" />
            <span className="mute">{solved} / {picked.length} solved</span>
          </div>
          <div className="pbar"><div style={{ width: `${(solved / picked.length) * 100}%` }} /></div>
          {picked.map((p) => (
            <Link key={p.slug} href={`/problems/${p.slug}`} className="card revrow">
              <span aria-hidden="true">{p.status === "SOLVED" ? "✅" : p.status === "ATTEMPTED" ? "🟡" : "⬜"}</span>
              <b className="grow" style={{ display: "inline", fontSize: 15 }}>{p.title}</b>
              <span className={p.difficulty} style={{ fontSize: 12 }}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
            </Link>
          ))}
          {solved === picked.length && <p className="mute">Session complete. Start another one.</p>}
        </section>
      )}
    </>
  );
}
