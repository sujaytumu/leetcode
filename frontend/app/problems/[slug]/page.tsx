"use client";
import dynamic from "next/dynamic";
import Markdown from "react-markdown";
import { type ComponentType, use, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  api, apiWithWake, ApiError, ExecutionStatus, Lang, ProblemDetail, ProblemSummary, RunResponse,
  Submission,
} from "@/lib/api";
import { STUDY } from "@/lib/study";
import { loadAll, recordAccepted, swr } from "@/lib/local";

import type { EditorProps } from "@monaco-editor/react";
// Without this, next/dynamic infers ComponentType<never> for Monaco's Editor and the production build fails type-checking.
const Editor = dynamic<EditorProps>(
  () => import("@monaco-editor/react").then((m) => m.default as unknown as ComponentType<EditorProps>), {
  ssr: false, loading: () => <p className="mute" style={{ padding: 16 }}>Loading editor…</p>,
});
const LANGS: { key: Lang; label: string; monaco: string }[] = [
  { key: "java", label: "Java", monaco: "java" }, { key: "python", label: "Python", monaco: "python" },
  { key: "javascript", label: "JavaScript", monaco: "javascript" }, { key: "cpp", label: "C++", monaco: "cpp" },
];
const title = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

export default function ProblemPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loadError, setLoadError] = useState("");
  const [waking, setWaking] = useState(false);
  const [lang, setLang] = useState<Lang>("java");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [mode, setMode] = useState<"run" | "submit">("run");
  const [busy, setBusy] = useState<"" | "run" | "submit">("");
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const [caseTab, setCaseTab] = useState(0);
  const [tab, setTab] = useState<"desc" | "history" | "notes">("desc");
  const [notes, setNotes] = useState("");
  const [stale, setStale] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [history, setHistory] = useState<Submission[]>([]);
  const [exec, setExec] = useState<ExecutionStatus | null>(null);
  const [all, setAll] = useState<ProblemSummary[]>([]);
  const [hintsShown, setHintsShown] = useState(0);
  const [showApproach, setShowApproach] = useState(false);
  const [timer, setTimer] = useState({ on: false, secs: 0 });

  const draftKey = (l: Lang) => `lc-draft:${slug}:${l}`;
  const loadHistory = useCallback(
    () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {}), [slug]);
  const checkExec = useCallback(
    () => api<ExecutionStatus>("/api/execution/status", {}, 20000).then(setExec)
      .catch((e: ApiError) => setExec({ enabled: true, reachable: false, provider: "unknown", message: e.message })), []);

  const loadProblem = useCallback(() => {
    setLoadError("");
    swr<ProblemDetail>(`/api/problems/${slug}`, (p, fromCache) => {
      setProblem(p); setStale(fromCache); if (!fromCache) setWaking(false);
    }, () => setWaking(true))
      .catch((e) => { setLoadError(e.message); setWaking(false); });
  }, [slug]);

  useEffect(() => { loadProblem(); loadHistory(); checkExec(); }, [loadProblem, loadHistory, checkExec]);
  useEffect(() => { loadAll((items) => setAll(items), () => {}).catch(() => {}); }, []);
  useEffect(() => {
    const l = localStorage.getItem("lc-lang") as Lang | null;
    if (l && LANGS.some((x) => x.key === l)) setLang(l);
    const f = Number(localStorage.getItem("lc-font"));
    if (f >= 11 && f <= 24) setFontSize(f);
  }, []);
  useEffect(() => { setNotes(localStorage.getItem(`lc-notes:${slug}`) ?? ""); }, [slug]);
  useEffect(() => { setHintsShown(0); setShowApproach(false); setTimer({ on: false, secs: 0 }); }, [slug]);
  useEffect(() => {
    if (!timer.on) return;
    const t = setInterval(() => setTimer((x) => ({ ...x, secs: x.secs + 1 })), 1000);
    return () => clearInterval(t);
  }, [timer.on]);

  useEffect(() => {
    if (problem) setCode(localStorage.getItem(draftKey(lang)) ?? problem.starterCode[lang] ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problem, lang]);

  useEffect(() => {
    if (!busy) return;
    setElapsed(0);
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [busy]);

  const onChange = (v?: string) => { setCode(v ?? ""); localStorage.setItem(draftKey(lang), v ?? ""); };

  const run = useCallback(async (kind: "run" | "submit") => {
    if (busy) return;
    setBusy(kind); setError(""); setMode(kind); setResult(null); setCaseTab(0);
    try {
      const r = await api<RunResponse>(`/api/problems/${slug}/${kind}`,
        { method: "POST", body: JSON.stringify({ language: lang, code }) }, 120000);
      setResult(r);
      if (kind === "submit" && r.verdict === "ACCEPTED") recordAccepted();
      const firstFail = r.cases.findIndex((c) => !c.passed);
      setCaseTab(firstFail >= 0 ? firstFail : 0);
      if (kind === "submit") loadHistory();
      checkExec();
    } catch (e) {
      setError((e as Error).message);
      checkExec();
    } finally { setBusy(""); }
  }, [busy, slug, lang, code, loadHistory, checkExec]);

  const runRef = useRef(run);
  runRef.current = run;
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "'") { e.preventDefault(); runRef.current("run"); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runRef.current("submit"); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  async function toggleBookmark() {
    if (!problem) return;
    try {
      await api(`/api/problems/${slug}/bookmark`, { method: problem.bookmarked ? "DELETE" : "PUT" });
      setProblem({ ...problem, bookmarked: !problem.bookmarked });
    } catch (e) { setError((e as Error).message); }
  }

  function reset() {
    if (!problem) return;
    localStorage.removeItem(draftKey(lang)); setCode(problem.starterCode[lang] ?? "");
  }

  if (!problem) {
    return (
      <>
        {waking && <div className="banner warn">Waking up the server (free hosting sleeps when idle). Retrying automatically — up to ~3 minutes…</div>}
        {loadError && <div className="banner err">{loadError} <button onClick={loadProblem}>Retry</button></div>}
        {!waking && !loadError && <p className="mute">Loading…</p>}
      </>
    );
  }

  const execDown = exec && (!exec.enabled || !exec.reachable);
  const study = STUDY[slug];
  const idx = all.findIndex((p) => p.slug === slug);
  const prev = idx > 0 ? all[idx - 1] : null;
  const next = idx >= 0 && idx + 1 < all.length ? all[idx + 1] : null;
  const clock = `${String(Math.floor(timer.secs / 60)).padStart(2, "0")}:${String(timer.secs % 60).padStart(2, "0")}`;
  const cur = result?.cases[caseTab];

  return (
    <>
      {stale && <div className="banner warn">Showing a saved copy while the server wakes up (1–3 min). Run and Submit work once it is back.</div>}
      {execDown && (
        <div className="banner warn">
          Code execution is unavailable: {exec.message} Run and Submit will show an error until it is back.
          <button onClick={checkExec}>Re-check</button>
        </div>
      )}
      <div className="split">
        <section className="pane">
          <div className="tabs">
            <button className={tab === "desc" ? "on" : ""} onClick={() => setTab("desc")}>Description</button>
            <button className={tab === "history" ? "on" : ""} onClick={() => { setTab("history"); loadHistory(); }}>Submissions</button>
            <button className={tab === "notes" ? "on" : ""} onClick={() => setTab("notes")}>Notes{notes ? " •" : ""}</button>
            <span className="grow" />
            {prev ? <Link className="navbtn" href={`/problems/${prev.slug}`} title={prev.title}>← Prev</Link> : <span className="navbtn off">← Prev</span>}
            {next ? <Link className="navbtn" href={`/problems/${next.slug}`} title={next.title}>Next →</Link> : <span className="navbtn off">Next →</span>}
            <button onClick={() => setTimer((x) => ({ ...x, on: !x.on }))} title="Stopwatch for this attempt">
              ⏱ {clock}{timer.on ? " ⏸" : timer.secs ? " ▶" : ""}
            </button>
            <button onClick={toggleBookmark}>{problem.bookmarked ? "★ Bookmarked" : "☆ Bookmark"}</button>
          </div>
          {tab === "desc" ? (
            <>
              <h2>{problem.id}. {problem.title}</h2>
              <p><span className={problem.difficulty}>{title(problem.difficulty)}</span>{" "}
                {problem.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</p>
              <div className="md"><Markdown>{problem.description}</Markdown></div>
              {study && (
                <div className="study">
                  <h3>Hints</h3>
                  {study.hints.slice(0, hintsShown).map((h, i) => (
                    <div className="hint" key={i}><b>Hint {i + 1}.</b> {h}</div>
                  ))}
                  {hintsShown < study.hints.length ? (
                    <button onClick={() => setHintsShown(hintsShown + 1)}>
                      {hintsShown === 0 ? "Show a hint" : `Show hint ${hintsShown + 1} of ${study.hints.length}`}
                    </button>
                  ) : <span className="mute">No more hints.</span>}
                  <h3>Approach</h3>
                  {showApproach ? (
                    <>
                      <p>{study.approach}</p>
                      <p className="mute">Time: <b>{study.time}</b> · Space: <b>{study.space}</b></p>
                    </>
                  ) : (
                    <button onClick={() => setShowApproach(true)}>Reveal approach (spoiler)</button>
                  )}
                </div>
              )}
            </>
          ) : tab === "notes" ? (
            <>
              <p className="mute" style={{ marginBottom: 6 }}>Private notes for this problem, saved on this device.</p>
              <textarea className="notes" placeholder="Your approach, mistakes, edge cases to remember…" value={notes}
                onChange={(e) => { setNotes(e.target.value); localStorage.setItem(`lc-notes:${slug}`, e.target.value); }} />
            </>
          ) : (
            <table style={{ marginTop: 12 }}>
              <thead><tr><th>Result</th><th>Lang</th><th>Tests</th><th>Time</th><th>When</th><th></th></tr></thead>
              <tbody>
                {history.map((s) => (
                  <tr key={s.id}>
                    <td className={s.verdict}>{title(s.verdict)}</td><td>{s.language}</td>
                    <td>{s.passed}/{s.total}</td><td>{s.runtimeMs ?? "-"} ms</td>
                    <td className="mute">{new Date(s.createdAt).toLocaleString()}</td>
                    <td><button onClick={() => { setLang(s.language); setCode(s.code); setTab("desc"); }}>Load</button></td>
                  </tr>
                ))}
                {history.length === 0 && <tr><td colSpan={6} className="mute">No submissions yet.</td></tr>}
              </tbody>
            </table>
          )}
        </section>
        <section className="col">
          <div className="bar actionbar">
            <select value={lang} onChange={(e) => { setLang(e.target.value as Lang); localStorage.setItem("lc-lang", e.target.value); }}>
              {LANGS.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
            </select>
            <select value={fontSize} title="Editor font size" onChange={(e) => { setFontSize(Number(e.target.value)); localStorage.setItem("lc-font", e.target.value); }}>
              {[12, 14, 16, 18, 20].map((n) => <option key={n} value={n}>{n}px</option>)}
            </select>
            <button onClick={reset} title="Reset to starter code">Reset</button><span className="grow" />
            <button disabled={!!busy} onClick={() => run("run")} title="Ctrl/⌘ + '">
              {busy === "run" ? `Running… ${elapsed}s` : "▶ Run"}
            </button>
            <button className="primary" disabled={!!busy} onClick={() => run("submit")} title="Ctrl/⌘ + Enter">
              {busy === "submit" ? `Judging… ${elapsed}s` : "Submit"}
            </button>
          </div>
          <div className="pane editor-pane" style={{ padding: 0, flex: 3 }}>
            <Editor height="100%" theme="vs-dark" language={LANGS.find((l) => l.key === lang)!.monaco}
              value={code} onChange={onChange}
              options={{ minimap: { enabled: false }, fontSize, automaticLayout: true, scrollBeyondLastLine: false }} />
          </div>
          <div className="pane result-pane" style={{ flex: 2 }}>
            {busy && (
              <span className="mute">
                {busy === "run" ? "Running your code on the sample cases" : "Judging against all test cases"}… {elapsed}s
                {elapsed > 20 && " (the free judge can be slow — hang on)"}
              </span>
            )}
            {error && !busy && <div className="banner err" style={{ margin: 0 }}>{error}</div>}
            {result && !busy && (
              <>
                <h3 className={result.verdict} style={{ margin: "0 0 4px" }}>{title(result.verdict)}</h3>
                <div className="mute" style={{ marginBottom: 8 }}>
                  {result.passed} / {result.total} testcases passed
                  {result.runtimeMs != null ? ` · Runtime: ${result.runtimeMs} ms` : ""}
                  {mode === "run" ? " · sample cases only" : ""}
                </div>
                {result.message && <div className={result.verdict === "ACCEPTED" ? "" : "err"}>{result.message}</div>}
                {result.cases.length > 0 && (
                  <div className="tabs" style={{ margin: "8px 0" }}>
                    {result.cases.map((c, i) => (
                      <button key={i} className={caseTab === i ? "on" : ""} onClick={() => setCaseTab(i)}>
                        <span className={c.passed ? "ACCEPTED" : "WRONG_ANSWER"}>●</span> {c.sample ? `Case ${c.index}` : `Hidden ${c.index}`}
                      </button>
                    ))}
                  </div>
                )}
                {cur && (cur.input != null ? (
                  <>
                    <div className="mute">Input</div><pre>{cur.input}</pre>
                    <div className="mute">Output</div><pre>{cur.actual || "(empty)"}</pre>
                    <div className="mute">Expected</div><pre>{cur.expected}</pre>
                    {cur.error && <><div className="mute">Error</div><pre className="err">{cur.error}</pre></>}
                  </>
                ) : (
                  <>
                    <div className="mute">Hidden test case — details are not shown.</div>
                    {cur.error && <pre className="err">{cur.error}</pre>}
                  </>
                ))}
              </>
            )}
            {!result && !busy && !error && <span className="mute">Run or submit to see results. Shortcuts: Ctrl/⌘+' to run, Ctrl/⌘+Enter to submit.</span>}
          </div>
        </section>
      </div>
    </>
  );
}
