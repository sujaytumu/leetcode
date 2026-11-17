"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { dailyIndex, ProblemSummary } from "@/lib/api";
import { useCatalog } from "@/lib/catalog";
import Activity from "@/components/Activity";
import Donut from "@/components/Donut";
import { StatusIcon } from "@/components/icons";

const PAGE_SIZE = 50;
const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

export default function Home() {
  const { items, ready, server, retry, loadError } = useCatalog();
  const router = useRouter();
  const [q, setQ] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [tag, setTag] = useState("");
  const [status, setStatus] = useState("");
  const [bookmarked, setBookmarked] = useState(false);
  const [page, setPage] = useState(0);

  const tags = useMemo(() => [...new Set(items.flatMap((p) => p.tags))].sort(), [items]);
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return items.filter((p) =>
      (!needle || p.title.toLowerCase().includes(needle) || String(p.id) === needle) &&
      (!difficulty || p.difficulty === difficulty) && (!tag || p.tags.includes(tag)) &&
      (!status || p.status === status) && (!bookmarked || p.bookmarked));
  }, [items, q, difficulty, tag, status, bookmarked]);

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const cur = Math.min(page, pages - 1);
  const rows = filtered.slice(cur * PAGE_SIZE, cur * PAGE_SIZE + PAGE_SIZE);
  const reset = <T,>(set: (v: T) => void) => (v: T) => { setPage(0); set(v); };

  const stats = useMemo(() => {
    const by = { EASY: { total: 0, solved: 0 }, MEDIUM: { total: 0, solved: 0 }, HARD: { total: 0, solved: 0 } };
    let attempted = 0;
    for (const p of items) { by[p.difficulty].total++; if (p.status === "SOLVED") by[p.difficulty].solved++; if (p.status === "ATTEMPTED") attempted++; }
    return { by, attempted, solved: by.EASY.solved + by.MEDIUM.solved + by.HARD.solved };
  }, [items]);

  const daily: ProblemSummary | null = items.length ? items[dailyIndex(items.length)] : null;
  const pickRandom = () => {
    const unsolved = items.filter((p) => p.status !== "SOLVED");
    const pool = unsolved.length ? unsolved : items;
    if (pool.length) router.push(`/problems/${pool[Math.floor(Math.random() * pool.length)].slug}`);
  };

  return (
    <main className="page">
      {loadError && <div className="banner err">Could not load the problem list ({loadError}). <button onClick={() => location.reload()}>Reload</button></div>}
      {server === "offline" && (
        <div className="banner warn">
          The server is not responding, so progress and Run/Submit are unavailable for now. Problems still open normally.
          <button onClick={retry}>Retry</button>
        </div>
      )}
      <div className="home-grid">
        <section>
          <div className="topics">
            <button className={tag === "" ? "on" : ""} onClick={() => reset(setTag)("")}>All Topics</button>
            {tags.map((t) => (
              <button key={t} className={tag === t ? "on" : ""} onClick={() => reset(setTag)(tag === t ? "" : t)}>{t}</button>
            ))}
          </div>
          <div className="toolbar">
            <div className="search">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
              <input placeholder="Search questions" value={q} onChange={(e) => reset(setQ)(e.target.value)} aria-label="Search questions" />
            </div>
            <select value={difficulty} onChange={(e) => reset(setDifficulty)(e.target.value)} aria-label="Difficulty">
              <option value="">Difficulty</option><option value="EASY">Easy</option><option value="MEDIUM">Medium</option><option value="HARD">Hard</option>
            </select>
            <select value={status} onChange={(e) => reset(setStatus)(e.target.value)} aria-label="Status">
              <option value="">Status</option><option value="TODO">Todo</option><option value="ATTEMPTED">Attempted</option><option value="SOLVED">Solved</option>
            </select>
            <select value={tag} onChange={(e) => reset(setTag)(e.target.value)} aria-label="Tags">
              <option value="">Tags</option>{tags.map((t) => <option key={t}>{t}</option>)}
            </select>
            <label className="chk"><input type="checkbox" checked={bookmarked} onChange={(e) => reset(setBookmarked)(e.target.checked)} /> Bookmarked</label>
            <span className="grow" />
            <button onClick={pickRandom} disabled={!items.length} title="Open a random problem you have not solved yet">🎲 Pick One</button>
          </div>

          <table className="ptable">
            <thead><tr><th>Status</th><th>Title</th><th className="tg">Topics</th><th className="acc">Acceptance</th><th className="dif">Difficulty</th></tr></thead>
            <tbody>
              {!ready && !loadError && Array.from({ length: 10 }, (_, i) => (
                <tr className="skeleton" key={i}><td><div style={{ width: 16, margin: "0 auto" }} /></td><td><div style={{ width: `${40 + (i * 13) % 35}%` }} /></td><td className="tg"><div style={{ width: "50%" }} /></td><td className="acc"><div style={{ width: 36, marginLeft: "auto" }} /></td><td><div style={{ width: 50 }} /></td></tr>
              ))}
              {rows.map((p) => (
                <tr key={p.slug}>
                  <td><StatusIcon status={p.status} /></td>
                  <td><Link className="ttl" href={`/problems/${p.slug}`}>{p.id}. {p.title}</Link>{p.bookmarked && <span title="Bookmarked" style={{ color: "var(--accent)", marginLeft: 6 }}>★</span>}</td>
                  <td className="tg mute" style={{ fontSize: 12 }}>{p.tags.slice(0, 3).join(" · ")}</td>
                  <td className="acc">{p.acceptance != null ? `${p.acceptance.toFixed(1)}%` : "–"}</td>
                  <td className={`dif ${p.difficulty}`}>{cap(p.difficulty)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {ready && rows.length === 0 && <div className="empty">No problems match your filters.</div>}
          {pages > 1 && (
            <div className="pager">
              <button disabled={cur === 0} onClick={() => setPage(cur - 1)}>Prev</button>
              <span className="mute">Page {cur + 1} of {pages}</span>
              <button disabled={cur + 1 >= pages} onClick={() => setPage(cur + 1)}>Next</button>
            </div>
          )}
        </section>

        <aside className="side">
          <div className="side-card wide">
            <h4>Progress</h4>
            <div className="donut-row">
              <Donut by={stats.by} solved={stats.solved} total={items.length} attempted={stats.attempted} />
              <div className="dstats">
                {(["EASY", "MEDIUM", "HARD"] as const).map((d) => (
                  <div className="dstat" key={d}><span className={d}>{cap(d)}</span><b>{stats.by[d].solved}/{stats.by[d].total}</b></div>
                ))}
              </div>
            </div>
            {server !== "online" && server !== "offline" && <div className="mute" style={{ fontSize: 12, marginTop: 10 }}>Syncing your progress — the server is waking up.</div>}
          </div>
          {daily && (
            <div className="side-card daily-card">
              <h4>Daily Challenge · {new Date().toLocaleDateString(undefined, { month: "short", day: "numeric" })}</h4>
              <Link href={`/problems/${daily.slug}`} className="dtitle">{daily.id}. {daily.title}</Link>
              <span className={`pill ${daily.difficulty}`}>{cap(daily.difficulty)}</span>
              {daily.status === "SOLVED" && <span className="EASY" style={{ marginLeft: 8, fontSize: 12 }}>✔ Solved</span>}
            </div>
          )}
          <div className="side-card wide"><h4>Streak</h4><Activity /></div>
        </aside>
      </div>
    </main>
  );
}
