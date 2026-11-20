"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, Daily, tagLabel, fetchAllProblems, localDate, Page, Progress, ProblemSummary } from "@/lib/api";
import { swr } from "@/lib/local";
import Activity from "@/components/Activity";
import WeeklyGoal from "@/components/WeeklyGoal";
import ContinueCard from "@/components/ContinueCard";
import SolvedCard from "@/components/SolvedCard";
import Skeleton from "@/components/Skeleton";
import FreeSpace from "@/components/FreeSpace";
import { useMeta } from "@/lib/meta";
import { FILTER_KEY, parseFilters } from "@/lib/listFilters";

const ICON = {
  SOLVED: <span className="st-done" title="Solved" aria-label="Solved">✔</span>,
  ATTEMPTED: <span className="st-att" title="Attempted" aria-label="Attempted" />,
  TODO: null,
} as const;

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
  const [counts, setCounts] = useState<Map<string, number>>(new Map());
  const [allTopics, setAllTopics] = useState(false);
  const [sheet, setSheet] = useState(false); // phone filter bottom sheet
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
  const [cursor, setCursor] = useState(-1);
  const tbodyRef = useRef<HTMLTableSectionElement>(null);
  // Come back to the filters and sort you left; a /?tag= link from the Topics page still wins for the topic.
  const [filtersReady, setFiltersReady] = useState(false);
  useEffect(() => {
    try {
      const f = parseFilters(localStorage.getItem(FILTER_KEY));
      const fromLink = new URLSearchParams(window.location.search).get("tag");
      if (f.difficulty !== undefined) setDifficulty(f.difficulty);
      if (f.status !== undefined) setStatus(f.status);
      if (f.tag !== undefined && !fromLink) setTag(f.tag);
      if (f.sort !== undefined) setSort(f.sort);
      if (f.dir !== undefined) setDir(f.dir);
      if (f.bookmarked !== undefined) setBookmarked(f.bookmarked);
    } catch { /* storage blocked: start with defaults */ }
    setFiltersReady(true);
  }, []);
  useEffect(() => {
    if (!filtersReady) return;
    try { localStorage.setItem(FILTER_KEY, JSON.stringify({ difficulty, tag, status, sort, dir, bookmarked })); } catch { /* storage blocked */ }
  }, [filtersReady, difficulty, tag, status, sort, dir, bookmarked]);
  const anyFilter = !!(q || difficulty || tag || status || sort || bookmarked);
  const clearFilters = () => { setQ(""); setDifficulty(""); setTag(""); setStatus(""); setSort(""); setDir("asc"); setBookmarked(false); setPage(0); };
  // /?tag=hash-table (from the Topics page) preselects that topic. lc-tag-init
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("tag");
    if (t) setTag(t);
  }, []);

  useEffect(() => {
    swr<string[]>("/api/tags", (t) => setTags(t), () => {}).catch(() => {});
    swr<{ tag: string; total: number }[]>("/api/topics", (t) => setCounts(new Map(t.map((x) => [x.tag, x.total]))), () => {}).catch(() => {});
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

  // Keyboard-first browsing on laptops: j/k move the highlight, Enter opens, r opens a random unsolved problem.
  const rows = data?.items ?? [];
  useEffect(() => { setCursor(-1); }, [data]);
  const kb = useRef({ rows, cursor, pickRandom });
  kb.current = { rows, cursor, pickRandom };
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const t = e.target as HTMLElement | null;
      if (t && (t.isContentEditable || t.closest("input, textarea, select, button, a, [role=dialog]"))) return;
      const { rows: r, cursor: c } = kb.current;
      const move = (to: number) => {
        e.preventDefault();
        setCursor(to);
        tbodyRef.current?.querySelectorAll("tr")[to]?.scrollIntoView({ block: "nearest" });
      };
      if (e.key === "j" && r.length) move(Math.min(r.length - 1, c + 1));
      else if (e.key === "k" && r.length) move(Math.max(0, c - 1));
      else if (e.key === "Enter" && c >= 0 && r[c]) { e.preventDefault(); router.push(`/problems/${r[c].slug}`); }
      else if (e.key === "r") { e.preventDefault(); kb.current.pickRandom(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [router]);

  const reset = <T,>(set: (v: T) => void) => (v: T) => { setPage(0); set(v); };

  return (
    <>
      <div className="home">
        <div className="home-main">
          <div className="chips lcchips">
            <button className={tag === "" ? "on" : ""} onClick={() => reset(setTag)("")}>All Topics</button>
            {(allTopics ? tags : [...tags].sort((a, b) => (counts.get(b) ?? 0) - (counts.get(a) ?? 0)).slice(0, 10)).map((t) => (
              <button key={t} className={tag === t ? "on" : ""} onClick={() => reset(setTag)(tag === t ? "" : t)}>
                {tagLabel(t)}{counts.has(t) && <span className="chipn">{counts.get(t)}</span>}
              </button>
            ))}
            {tags.length > 10 && <button type="button" className="chipmore" onClick={() => setAllTopics((v) => !v)}>{allTopics ? "Collapse ▴" : "Expand ▾"}</button>}
          </div>
          <div className="filters">
            <input className="grow" placeholder="Search problems…" value={q} onChange={(e) => reset(setQ)(e.target.value)} />
            <button type="button" className="ftoggle" onClick={() => setSheet(true)} aria-label="Open filters">
              <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M3 5h18M6 12h12M10 19h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" /></svg>
              {[difficulty, tag, status, bookmarked ? "b" : ""].filter(Boolean).length > 0 && <span className="fcount">{[difficulty, tag, status, bookmarked ? "b" : ""].filter(Boolean).length}</span>}
            </button>
            {sheet && <div className="fback" onClick={() => setSheet(false)} aria-hidden="true" />}
            <div className={`fsheet${sheet ? " open" : ""}`} role={sheet ? "dialog" : undefined} aria-label="Filters">
              <div className="fsheet-head"><b>Filters</b><button type="button" className="fdone" onClick={() => setSheet(false)}>Done</button></div>
              <select value={difficulty} onChange={(e) => reset(setDifficulty)(e.target.value)}>
                <option value="">All difficulties</option>
                {meta?.difficulties.map((d) => <option key={d.key} value={d.key}>{d.label}</option>)}
              </select>
              <select value={tag} onChange={(e) => reset(setTag)(e.target.value)}>
                <option value="">All topics</option>{tags.map((t) => <option key={t} value={t}>{tagLabel(t)}</option>)}
              </select>
              <select value={status} onChange={(e) => reset(setStatus)(e.target.value)}>
                <option value="">Any status</option>
                {meta?.statuses.map((x) => <option key={x.key} value={x.key}>{x.label}</option>)}
              </select>
              <label className="bar"><input type="checkbox" checked={bookmarked}
                onChange={(e) => reset(setBookmarked)(e.target.checked)} /> Bookmarked</label>
              {anyFilter && <button type="button" onClick={clearFilters} title="Reset every filter and the sort order">Clear filters</button>}
            </div>
          </div>
          <table>
            <thead><tr><th style={{ width: 40 }}></th><th aria-sort={ariaSort("title")}><button className="sorth" onClick={() => toggleSort("title")}>Title{arrow("title")}</button></th><th className="hide-sm">Topics</th><th className="th-num col-acc" aria-sort={ariaSort("acceptance")}><button className="sorth" onClick={() => toggleSort("acceptance")}>Acceptance{arrow("acceptance")}</button></th><th aria-sort={ariaSort("difficulty")}><button className="sorth" onClick={() => toggleSort("difficulty")}>Difficulty{arrow("difficulty")}</button></th></tr></thead>
            <tbody ref={tbodyRef}>
              {data?.items.map((p, i) => (
                <tr key={p.id} className={i === cursor ? "kbrow" : undefined}>
                  <td className={p.status === "ATTEMPTED" ? "MEDIUM" : "EASY"}>{ICON[p.status]}</td>
                  <td><Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}{p.bookmarked ? " ★" : ""}</Link>
                    <div className="show-sm"><span className={`${p.difficulty} sm-diff`}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>{p.acceptance != null && <span className="mute sm-acc">{p.acceptance.toFixed(1)}%</span>}{p.tags.slice(0, 3).map((t) => <span className="tag" key={t}>{tagLabel(t)}</span>)}</div></td>
                  <td className="hide-sm">{p.tags.map((t) => <span className="tag" key={t}>{tagLabel(t)}</span>)}</td>
                  <td className="th-num col-acc mute">{p.acceptance != null ? `${p.acceptance.toFixed(1)}%` : "–"}</td>
                  <td className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</td>
                </tr>
              ))}
              {!loading && !error && data?.items.length === 0 && <tr><td colSpan={5} className="mute">No problems match.</td></tr>}
            </tbody>
          </table>
          {rows.length > 0 && (
            <p className="mute kbhint hide-sm"><kbd>J</kbd> <kbd>K</kbd> move · <kbd>Enter</kbd> open · <kbd>R</kbd> random · <kbd>/</kbd> search</p>
          )}
          {!data && <FreeSpace loading={loading} error={error} onRetry={() => setReload((n) => n + 1)} label="Loading problems…" />}
          {data && error && (
            <div className="banner err" style={{ marginTop: 10 }}>
              {error} <button onClick={() => setReload((n) => n + 1)}>Retry</button>
            </div>
          )}
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
                <span className="mute"><Link href="/daily" className="mute" title="Daily challenge calendar">Daily challenge ▦</Link> · {new Date(`${dailyData!.date}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
                <div><Link href={`/problems/${daily.slug}`}><b style={{ display: "inline", fontSize: 15 }}>{daily.number ?? daily.id}. {daily.title}</b></Link>{" "}
                  <span className={daily.difficulty}>{daily.difficulty[0] + daily.difficulty.slice(1).toLowerCase()}</span>
                  {daily.status === "SOLVED" && <span className="EASY"> ✔ solved</span>}
                </div>
              </div>
              <span className="grow" />
              <button onClick={pickRandom} disabled={picking} title="Open a random problem you have not solved yet">🎲 Pick one</button>
            </div>
          )}
          <ContinueCard />
          <WeeklyGoal />
          <Activity />
        </aside>
      </div>
    </>
  );
}
