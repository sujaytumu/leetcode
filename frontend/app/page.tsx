"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, Page, Progress, ProblemSummary } from "@/lib/api";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "" } as const;

export default function Home() {
  const [q, setQ] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [tag, setTag] = useState("");
  const [status, setStatus] = useState("");
  const [bookmarked, setBookmarked] = useState(false);
  const [page, setPage] = useState(0);
  const [tags, setTags] = useState<string[]>([]);
  const [data, setData] = useState<Page<ProblemSummary> | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<string[]>("/api/tags").then(setTags).catch(() => {});
    api<Progress>("/api/progress").then(setProgress).catch(() => {});
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      const p = new URLSearchParams({ page: String(page), size: "20" });
      if (q) p.set("q", q); if (difficulty) p.set("difficulty", difficulty);
      if (tag) p.set("tag", tag); if (status) p.set("status", status);
      if (bookmarked) p.set("bookmarked", "true");
      setLoading(true);
      api<Page<ProblemSummary>>(`/api/problems?${p}`)
        .then((d) => { setData(d); setError(""); })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [q, difficulty, tag, status, bookmarked, page]);

  const reset = <T,>(set: (v: T) => void) => (v: T) => { setPage(0); set(v); };

  return (
    <>
      {progress && (
        <div className="cards">
          <div className="card"><span className="mute">Solved</span><b>{progress.solved}/{progress.total}</b></div>
          {(["EASY", "MEDIUM", "HARD"] as const).map((d) => (
            <div className="card" key={d}><span className={d}>{d}</span>
              <b>{progress.byDifficulty?.[d]?.solved ?? 0}/{progress.byDifficulty?.[d]?.total ?? 0}</b></div>
          ))}
          <div className="card"><span className="mute">Attempted</span><b>{progress.attempted}</b></div>
          <div className="card"><span className="mute">Bookmarked</span><b>{progress.bookmarked}</b></div>
        </div>
      )}
      <div className="filters">
        <input placeholder="Search problems…" value={q} onChange={(e) => reset(setQ)(e.target.value)} />
        <select value={difficulty} onChange={(e) => reset(setDifficulty)(e.target.value)}>
          <option value="">All difficulties</option><option value="EASY">Easy</option>
          <option value="MEDIUM">Medium</option><option value="HARD">Hard</option>
        </select>
        <select value={tag} onChange={(e) => reset(setTag)(e.target.value)}>
          <option value="">All topics</option>{tags.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select value={status} onChange={(e) => reset(setStatus)(e.target.value)}>
          <option value="">Any status</option><option value="TODO">Todo</option>
          <option value="ATTEMPTED">Attempted</option><option value="SOLVED">Solved</option>
        </select>
        <label className="bar"><input type="checkbox" checked={bookmarked}
          onChange={(e) => reset(setBookmarked)(e.target.checked)} /> Bookmarked</label>
      </div>
      {error && <p className="err">{error} — the API may be waking up (free tier), retry in ~50s.</p>}
      <table>
        <thead><tr><th style={{ width: 40 }}></th><th>Title</th><th>Topics</th><th>Difficulty</th></tr></thead>
        <tbody>
          {data?.items.map((p) => (
            <tr key={p.id}>
              <td className="EASY">{ICON[p.status]}</td>
              <td><Link href={`/problems/${p.slug}`}>{p.id}. {p.title}{p.bookmarked ? " ★" : ""}</Link></td>
              <td>{p.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</td>
              <td className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</td>
            </tr>
          ))}
          {!loading && data?.items.length === 0 && <tr><td colSpan={4} className="mute">No problems match.</td></tr>}
          {loading && !data && <tr><td colSpan={4} className="mute">Loading…</td></tr>}
        </tbody>
      </table>
      {data && data.totalPages > 1 && (
        <div className="pager">
          <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
          <span className="mute">Page {data.page + 1} / {data.totalPages}</span>
          <button disabled={page + 1 >= data.totalPages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </>
  );
}
