"use client";
import Link from "next/link";
import { memo, useCallback, useEffect, useState } from "react";
import { Page, ProblemSummary, tagLabel } from "@/lib/api";
import { prefetchProblem, swr } from "@/lib/local";
import FreeSpace from "@/components/FreeSpace";
import { SHEETS, Sheet, compareTopics, sheetFromParam, topicOf } from "@/lib/sheets";
import "../striver.css";

const SHEET_KEY = "lc-striver-sheet";
const TICK_KEY = "lc-striver-done";
const ICON = {
  SOLVED: <span className="st-done" title="Solved" aria-label="Solved">✔</span>,
  ATTEMPTED: <span className="st-att" title="Attempted" aria-label="Attempted" />,
  TODO: null,
} as const;
const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

/** One row of the sheet. Memoised so ticking a problem re-renders that row only, not the whole sheet. */
const SheetRow = memo(function SheetRow({ p, d, done, ticked, onToggle }: { p: ProblemSummary; d: string; done: boolean; ticked: boolean; onToggle: (slug: string) => void }) {
  return (
    <li className={`sh-row ${d}`}>
                          <label className={`sh-check${p.status === "ATTEMPTED" && !done ? " att" : ""}`} title={p.status === "SOLVED" ? "Solved by a submission" : ticked ? "Marked done (tap to undo)" : "Mark as done"}>
                            <input type="checkbox" checked={done} disabled={p.status === "SOLVED"} onChange={() => onToggle(p.slug)} aria-label={`Mark ${p.title} as done`} />
                            <i aria-hidden="true" />
                          </label>
                          <Link prefetch={false} className="sh-title" href={`/problems/${p.slug}?lang=cpp`} onPointerEnter={() => prefetchProblem(p.slug)} onTouchStart={() => prefetchProblem(p.slug)}>{p.number ?? p.id}. {p.title}</Link>
                          <span className={`sh-diff ${p.difficulty}`}>{cap(p.difficulty)}</span>
                          <Link prefetch={false} href={`/problems/${p.slug}?lang=cpp`} className="sh-btn sh-solve" aria-label={`Solve ${p.title}`}>Solve</Link>
                          <Link prefetch={false} href={`/problems/${p.slug}?tab=solutions&lang=cpp`} className="sh-btn sh-sol" title="C++ solution" aria-label={`C++ solution for ${p.title}`}>
                            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M7 3h7l5 5v13H7z M14 3v5h5 M10 13h6 M10 17h6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" /></svg>
                            <span>C++ solution</span>
                          </Link>
                        </li>
  );
});

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
  const [ticked, setTicked] = useState<Set<string>>(new Set()); // problems you ticked by hand, kept on this device

  // Which sheet: ?sheet=a2z|sde from a link, else the one you used last time.
  useEffect(() => {
    let s = sheetFromParam(new URLSearchParams(window.location.search).get("sheet"));
    if (!s) { try { s = sheetFromParam(localStorage.getItem(SHEET_KEY)); } catch { /* storage blocked */ } }
    if (s) setSheet(s);
    setReady(true);
  }, []);

  useEffect(() => {
    try { const raw = localStorage.getItem(TICK_KEY); if (raw) setTicked(new Set(JSON.parse(raw) as string[])); } catch { /* storage blocked */ }
  }, []);
  const toggleTick = useCallback((slug: string) => {
    setTicked((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug); else next.add(slug);
      try { localStorage.setItem(TICK_KEY, JSON.stringify([...next])); } catch { /* storage blocked */ }
      return next;
    });
  }, []);
  const isDone = (p: ProblemSummary) => p.status === "SOLVED" || ticked.has(p.slug);

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
  const solved = all.filter(isDone).length;
  const next = all.find((p) => !isDone(p));
  const text = q.trim().toLowerCase();
  const shown = all.filter((p) => (!difficulty || p.difficulty === difficulty) && (!hideSolved || !isDone(p)) && (!text || p.title.toLowerCase().includes(text)));
  const groupTotals = new Map<string, { solved: number; total: number }>();
  for (const p of all) {
    const t = topicOf(p), g = groupTotals.get(t) ?? { solved: 0, total: 0 };
    g.total++; if (isDone(p)) g.solved++;
    groupTotals.set(t, g);
  }
  const groups = new Map<string, ProblemSummary[]>();
  for (const p of shown) { const t = topicOf(p); groups.set(t, [...(groups.get(t) ?? []), p]); }

  return (
    <div className="sh">
      <header className="sh-head">
        <h1>Striver Sheets</h1>
        <p className="mute">Striver&apos;s sheets, topic by topic. Tick a problem when you are done, open the question to solve it in C++, and the answer shows the optimal C++ solution.</p>
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
            <div className="sh-bar" role="progressbar" aria-valuemin={0} aria-valuemax={all.length} aria-valuenow={solved} aria-label="Done on this sheet"><i style={{ width: `${(solved / all.length) * 100}%` }} /></div>
            <span className="sh-count"><b>{solved}</b> / {all.length} done{all.length > 0 && <> · {Math.round((solved / all.length) * 100)}%</>}</span>
          </div>
        )}
        {all.length > 0 && (
          <div className="sh-levels">
            {(["EASY", "MEDIUM", "HARD"] as const).map((l) => {
              const ps = all.filter((x) => x.difficulty === l);
              const dn = ps.filter(isDone).length;
              return (
                <div key={l} className={`sh-lv ${l}`}>
                  <span>{cap(l)}</span>
                  <b>{dn}<small> / {ps.length}</small></b>
                  <div className="sh-bar sm"><i style={{ width: `${ps.length ? (dn / ps.length) * 100 : 0}%` }} /></div>
                </div>
              );
            })}
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
          <label className="sh-hide"><input type="checkbox" checked={hideSolved} onChange={(e) => setHideSolved(e.target.checked)} /> Hide done</label>
        </div>
      )}

      {!all.length && <FreeSpace loading={loading} error={error} onRetry={() => setReload((n) => n + 1)} label="Loading the sheet…" />}
      {all.length > 0 && error && <div className="banner err">{error} <button onClick={() => setReload((n) => n + 1)}>Retry</button></div>}
      {all.length > 0 && shown.length === 0 && <p className="mute sh-empty">Nothing matches those filters.</p>}

      {[...groups.entries()].sort(([a], [b]) => compareTopics(a, b)).map(([topic, items]) => {
        const g = groupTotals.get(topic)!;
        return (
          <details className="sh-group" key={topic} open>
            <summary><span className="sh-gname">{tagLabel(topic)}</span><span className="sh-gcount">{g.solved}/{g.total}</span></summary>
            <ul className="sh-list">
              <li className="sh-cols" aria-hidden="true"><span>Done</span><span>Problem</span><span>Level</span><span>Question</span><span>Answer</span></li>
              {(["EASY", "MEDIUM", "HARD"] as const).map((d) => {
                const part = items.filter((p) => p.difficulty === d);
                if (!part.length) return null;
                const done = part.filter(isDone).length;
                return (
                  <li key={d} className="sh-levelwrap">
                    <div className={`sh-level ${d}`}><b>{cap(d)}</b><span>{done}/{part.length}</span></div>
                    <ul className="sh-sublist">
                      {part.map((p) => (
                        <SheetRow key={p.id} p={p} d={d} done={isDone(p)} ticked={ticked.has(p.slug)} onToggle={toggleTick} />
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
