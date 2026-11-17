"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, Daily, fetchAllProblems, localDate, Page, Progress, ProblemSummary } from "@/lib/api";
import { swr } from "@/lib/local";
import Activity from "@/components/Activity";
import SolvedCard from "@/components/SolvedCard";
import Skeleton from "@/components/Skeleton";
import { useMeta } from "@/lib/meta";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "" } as const;

export default function Home() {
  const [sort, setSort] = useState("");
  const [dir, setDir] = useState("asc");
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
  const [reload, setReload] = useState(0);
  const reqId = useRef(0);
  const [picking, setPicking] = useState(false);
  const [dailyData, setDailyData] = useState<Daily | null>(null);
  const router = useRouter();
  const meta = useMeta();

  useEffect(() => {
    swr<string[]>("/api/tags", (t) => setTags(t), () => {}).catch(() => {});
    swr<Progress>("/api/progress", (pr) => setProgress(pr), () => {}).catch(() => {});
    swr<Daily | undefined>(`/api/daily?date=${localDate()}`, (d) => setDailyData(d ?? null), () => {}).catch(() => {});
  }, [reload]);

  const daily = dailyData?.problem ?? null;
  const pickRandom = async () => {
    setPicking(true);
    try {
      const items = await fetchAllProblems();
      const unsolved = items.filter((p) => p.status !== "SOLVED");
      const pool = unsolved.length ? unsolved : items;
      if (pool.length) router.push(`/problems/${pool[Math.floor(Math.random() * pool.length)].slug}`);
    } catch { /* the nav indicator and list error banner already cover connectivity problems */ }
    finally { setPicking(false); }
  };

  const toggleSort = (key: string) => {
    setPage(0);
    if (sort !== key) { setSort(key); setDir("asc"); }
    else if (dir === "asc") setDir("desc");
    else { setSort(""); setDir("asc"); } // third click returns to the study-path order
  };
  const arrow = (key: string) => (sort === key ? (dir === "asc" ? " ▲" : " ▼") : "");
  const ariaSort = (key: string) => (sort === key ? (dir === "asc" ? "ascending" : "descending") : "none");

  const fetchList = useCallback(() => {
    const p = new URLSearchParams({ page: String(page) });
    if (q) p.set("q", q); if (difficulty) p.set("difficulty", difficulty);
    if (tag) p.set("tag", tag); if (status) p.set("status", status);
    if (bookmarked) p.set("bookmarked", "true");
    if (sort) { p.set("sort", sort); p.set("dir", dir); }
    setLoading(true); setError("");
    const my = ++reqId.current;
    swr<Page<ProblemSummary>>(`/api/problems?${p}`, (d) => {
      if (my === reqId.current) setData(d);
    }, () => {})
      .catch((e) => { if (my === reqId.current) setError(e.message); })
      .finally(() => { if (my === reqId.current) setLoading(false); });
  }, [q, difficulty, tag, status, bookmarked, page, sort, dir]);

  useEffect(() => {
    const t = setTimeout(fetchList, 250);
    return () => clearTimeout(t);
  }, [fetchList, reload]);

  const reset = <T,>(set: (v: T) => void) => (v: T) => { setPage(0); set(v); };

  return (
    <>
      {error && (
        <div className="banner err">
          {error} <button onClick={() => setReload((n) => n + 1)}>Retry</button>
        </div>
      )}
      <div className="home">
        <div className="home-main">
          <div className="chips">
            <button className={tag === "" ? "on" : ""} onClick={() => reset(setTag)("")}>All topics</button>
            {tags.map((t) => (
              <button key={t} className={tag === t ? "on" : ""} onClick={() => reset(setTag)(tag === t ? "" : t)}>{t}</button>
            ))}
          </div>
          <div className="filters">
            <input className="grow" placeholder="Search problems…" value={q} onChange={(e) => reset(setQ)(e.target.value)} />
            <select value={difficulty} onChange={(e) => reset(setDifficulty)(e.target.value)}>
              <option value="">All difficulties</option>
              {meta?.difficulties.map((d) => <option key={d.key} value={d.key}>{d.label}</option>)}
            </select>
            <select value={tag} onChange={(e) => reset(setTag)(e.target.value)}>
              <option value="">All topics</option>{tags.map((t) => <option key={t}>{t}</option>)}
            </select>
            <select value={status} onChange={(e) => reset(setStatus)(e.target.value)}>
              <option value="">Any status</option>
              {meta?.statuses.map((x) => <option key={x.key} value={x.key}>{x.label}</option>)}
            </select>
            <label className="bar"><input type="checkbox" checked={bookmarked}
              onChange={(e) => reset(setBookmarked)(e.target.checked)} /> Bookmarked</label>
          </div>
          <table>
            <thead><tr><th style={{ width: 40 }}></th><th aria-sort={ariaSort("title")}><button className="sorth" onClick={() => toggleSort("title")}>Title{arrow("title")}</button></th><th className="hide-sm">Topics</th><th className="th-num" aria-sort={ariaSort("acceptance")}><button className="sorth" onClick={() => toggleSort("acceptance")}>Acceptance{arrow("acceptance")}</button></th><th aria-sort={ariaSort("difficulty")}><button className="sorth" onClick={() => toggleSort("difficulty")}>Difficulty{arrow("difficulty")}</button></th></tr></thead>
            <tbody>
              {data?.items.map((p) => (
                <tr key={p.id}>
                  <td className={p.status === "ATTEMPTED" ? "MEDIUM" : "EASY"}>{ICON[p.status]}</td>
                  <td><Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}{p.bookmarked ? " ★" : ""}</Link>
                    <div className="show-sm">{p.tags.slice(0, 3).map((t) => <span className="tag" key={t}>{t}</span>)}</div></td>
                  <td className="hide-sm">{p.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</td>
                  <td className="th-num mute">{p.acceptance != null ? `${p.acceptance.toFixed(1)}%` : "–"}</td>
                  <td className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</td>
                </tr>
              ))}
              {!loading && !error && data?.items.length === 0 && <tr><td colSpan={5} className="mute">No problems match.</td></tr>}
              {loading && !data && Array.from({ length: 10 }, (_, i) => (
                <tr key={i}><td colSpan={5}><div className="skel" style={{ width: `${50 + ((i * 13) % 40)}%` }} /></td></tr>
              ))}
            </tbody>
          </table>
          {data && data.totalPages > 1 && (
            <div className="pager">
              <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
              <span className="mute">Page {data.page + 1} / {data.totalPages}</span>
              <button disabled={page + 1 >= data.totalPages} onClick={() => setPage(page + 1)}>Next</button>
            </div>
          )}
        </div>

        <aside className="home-side">
          {progress && meta ? (
            <SolvedCard progress={progress} attempting={Math.max(0, progress.attempted - progress.solved)} difficulties={meta.difficulties} />
          ) : <div className="card"><Skeleton lines={6} /></div>}
          {daily && (
            <div className="card daily">
              <div>
                <span className="mute">Daily challenge · {new Date(`${dailyData!.date}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
                <div><Link href={`/problems/${daily.slug}`}><b style={{ display: "inline", fontSize: 15 }}>{daily.number ?? daily.id}. {daily.title}</b></Link>{" "}
                  <span className={daily.difficulty}>{daily.difficulty[0] + daily.difficulty.slice(1).toLowerCase()}</span>
                  {daily.status === "SOLVED" && <span className="EASY"> ✔ solved</span>}
                </div>
              </div>
              <span className="grow" />
              <button onClick={pickRandom} disabled={picking} title="Open a random problem you have not solved yet">🎲 Pick one</button>
            </div>
          )}
          <Activity />
        </aside>
      </div>
    </>
  );
}
