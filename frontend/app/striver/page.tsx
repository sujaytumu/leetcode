"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Page, ProblemSummary, tagLabel } from "@/lib/api";
import { prefetchProblem, swr } from "@/lib/local";
import FreeSpace from "@/components/FreeSpace";
import { SHEETS, Sheet, sheetFromParam, topicOf } from "@/lib/sheets";
import "../striver.css";

const SHEET_KEY = "lc-striver-sheet";
const ICON = {
  SOLVED: <span className="st-done" title="Solved" aria-label="Solved">✔</span>,
  ATTEMPTED: <span className="st-att" title="Attempted" aria-label="Attempted" />,
  TODO: null,
} as const;
const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

/** Striver's A2Z and SDE sheets on one page: pick a sheet, see your progress, work through it topic by topic. */
export default function StriverPage() {
  const [sheet, setSheet] = useState<Sheet>(SHEETS[0]);
  const [ready, setReady] = useState(false);
  const [pages, setPages] = useState<Record<number, ProblemSummary[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [totals, setTotals] = useState<Map<string, number>>(new Map());
  const [difficulty, setDifficulty] = useState("");
  const [hideSolved, setHideSolved] = useState(false);
  const [q, setQ] = useState("");

  // Which sheet: ?sheet=a2z|sde from a link, else the one you used last time.
  useEffect(() => {
    let s = sheetFromParam(new URLSearchParams(window.location.search).get("sheet"));
    if (!s) { try { s = sheetFromParam(localStorage.getItem(SHEET_KEY)); } catch { /* storage blocked */ } }
    if (s) setSheet(s);
    setReady(true);
  }, []);

  useEffect(() => {
    swr<{ tag: string; total: number }[]>("/api/topics", (t) => setTotals(new Map(t.map((x) => [x.tag, x.total]))), () => {}).catch(() => {});
  }, []);

  useEffect(() => {
    if (!ready) return;
    let alive = true;
    setPages({}); setError(""); setLoading(true);
    const url = (n: number) => `/api/problems?tag=${sheet.tag}&page=${n}&size=100`;
    (async () => {
      let total = 1;
      await swr<Page<ProblemSummary>>(url(0), (d) => { total = d.totalPages; if (alive) setPages((p) => ({ ...p, 0: d.items })); }, () => {});
      await Promise.all(Array.from({ length: Math.max(0, total - 1) }, (_, i) =>
        swr<Page<ProblemSummary>>(url(i + 1), (d) => { if (alive) setPages((p) => ({ ...p, [i + 1]: d.items })); }, () => {})));
    })()
      .catch((e: Error) => { if (alive) setError(e.message || "Could not load the sheet"); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [ready, sheet, reload]);

  const choose = (s: Sheet) => {
    setSheet(s); setDifficulty(""); setHideSolved(false); setQ("");
    try { localStorage.setItem(SHEET_KEY, s.short); } catch { /* storage blocked */ }
    window.history.replaceState(null, "", `/striver?sheet=${s.short.toLowerCase()}`);
  };

  const all = Object.keys(pages).map(Number).sort((a, b) => a - b).flatMap((k) => pages[k]);
  const solved = all.filter((p) => p.status === "SOLVED").length;
  const next = all.find((p) => p.status !== "SOLVED");
  const text = q.trim().toLowerCase();
  const shown = all.filter((p) => (!difficulty || p.difficulty === difficulty) && (!hideSolved || p.status !== "SOLVED") && (!text || p.title.toLowerCase().includes(text)));
  const groupTotals = new Map<string, { solved: number; total: number }>();
  for (const p of all) {
    const t = topicOf(p), g = groupTotals.get(t) ?? { solved: 0, total: 0 };
    g.total++; if (p.status === "SOLVED") g.solved++;
    groupTotals.set(t, g);
  }
  const groups = new Map<string, ProblemSummary[]>();
  for (const p of shown) { const t = topicOf(p); groups.set(t, [...(groups.get(t) ?? []), p]); }

  return (
    <div className="sh">
      <header className="sh-head">
        <h1>Striver Sheets</h1>
        <p className="mute">Work through Striver&apos;s sheets topic by topic. Your progress is tracked as you solve.</p>
      </header>

      <div className="sh-tabs" role="tablist" aria-label="Choose a sheet">
        {SHEETS.map((s) => {
          const n = totals.get(s.tag) ?? (s.tag === sheet.tag && all.length ? all.length : undefined);
          return (
            <button key={s.tag} type="button" role="tab" aria-selected={s.tag === sheet.tag} className={s.tag === sheet.tag ? "on" : ""} onClick={() => choose(s)}>
              <b>{s.label}</b>{n !== undefined && <span className="sh-n">{n}</span>}
            </button>
          );
        })}
      </div>

      <section className="sh-card" aria-label={`${sheet.full} progress`}>
        <div className="sh-card-top">
          <div>
            <h2>{sheet.full}</h2>
            <p className="mute">{sheet.blurb}</p>
          </div>
          {all.length > 0 && (next
            ? <Link className="sh-go" href={`/problems/${next.slug}`}>{solved === 0 ? "Start" : "Continue"} →</Link>
            : <span className="sh-done">All solved 🎉</span>)}
        </div>
        {all.length > 0 && (
          <div className="sh-prog">
            <div className="sh-bar" role="progressbar" aria-valuemin={0} aria-valuemax={all.length} aria-valuenow={solved} aria-label="Solved on this sheet"><i style={{ width: `${(solved / all.length) * 100}%` }} /></div>
            <span className="sh-count"><b>{solved}</b> / {all.length} solved</span>
          </div>
        )}
      </section>

      {all.length > 0 && (
        <div className="sh-filters">
          <input placeholder="Search this sheet…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search this sheet" />
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} aria-label="Difficulty">
            <option value="">All difficulties</option>
            <option value="EASY">Easy</option><option value="MEDIUM">Medium</option><option value="HARD">Hard</option>
          </select>
          <label className="sh-hide"><input type="checkbox" checked={hideSolved} onChange={(e) => setHideSolved(e.target.checked)} /> Hide solved</label>
        </div>
      )}

      {!all.length && <FreeSpace loading={loading} error={error} onRetry={() => setReload((n) => n + 1)} label="Loading the sheet…" />}
      {all.length > 0 && error && <div className="banner err">{error} <button onClick={() => setReload((n) => n + 1)}>Retry</button></div>}
      {all.length > 0 && shown.length === 0 && <p className="mute sh-empty">Nothing matches those filters.</p>}

      {[...groups.entries()].map(([topic, items]) => {
        const g = groupTotals.get(topic)!;
        return (
          <details className="sh-group" key={topic} open>
            <summary><span className="sh-gname">{tagLabel(topic)}</span><span className="sh-gcount">{g.solved}/{g.total}</span></summary>
            <ul className="sh-list">
              {(["EASY", "MEDIUM", "HARD"] as const).map((d) => {
                const part = items.filter((p) => p.difficulty === d);
                if (!part.length) return null;
                const done = part.filter((p) => p.status === "SOLVED").length;
                return (
                  <li key={d} className="sh-levelwrap">
                    <div className={`sh-level ${d}`}><b>{cap(d)}</b><span>{done}/{part.length}</span></div>
                    <ul className="sh-sublist">
                      {part.map((p) => (
                        <li key={p.id} className={`sh-row ${d}`}>
                          <span className="sh-st">{ICON[p.status]}</span>
                          <Link className="sh-title" href={`/problems/${p.slug}`} onPointerEnter={() => prefetchProblem(p.slug)} onTouchStart={() => prefetchProblem(p.slug)}>{p.number ?? p.id}. {p.title}</Link>
                          <span className={`sh-diff ${p.difficulty}`}>{cap(p.difficulty)}</span>
                          <Link href={`/problems/${p.slug}?tab=solutions`} className="solico sh-sol" title="Solutions" aria-label={`Solutions for ${p.title}`}>
                            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 3h7l5 5v13H7z M14 3v5h5 M10 13h6 M10 17h6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" /></svg>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </li>
                );
              })}
            </ul>
          </details>
        );
      })}
    </div>
  );
}
