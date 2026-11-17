"use client";
import dynamic from "next/dynamic";
import Markdown from "react-markdown";
import { type ComponentType, type PointerEvent as RPointerEvent, use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { api, Lang, ProblemDetail, RunResponse, Submission, ExecutionStatus } from "@/lib/api";
import { STUDY } from "@/lib/study";
import { recordAccepted, swr } from "@/lib/local";
import { ensureAwake, fetchStaticProblem, StaticProblem, useCatalog } from "@/lib/catalog";
import { currentTheme, type ThemeName } from "@/components/ThemeToggle";
import { ChevronLeft, ChevronRight, CodeIcon, ListIcon, PlayIcon, } from "@/components/icons";
import { StatusIcon } from "@/components/icons";

import type { EditorProps } from "@monaco-editor/react";
// Without this, next/dynamic infers ComponentType<never> for Monaco's Editor and the production build fails type-checking.
const Editor = dynamic<EditorProps>(
  () => import("@monaco-editor/react").then((m) => m.default as unknown as ComponentType<EditorProps>), {
  ssr: false, loading: () => <p className="mute" style={{ padding: 16 }}>Loading editor…</p>,
});
const LANGS: { key: Lang; label: string; monaco: string }[] = [
  { key: "java", label: "Java", monaco: "java" }, { key: "python", label: "Python3", monaco: "python" },
  { key: "javascript", label: "JavaScript", monaco: "javascript" }, { key: "cpp", label: "C++", monaco: "cpp" },
];
const title = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));
const norm = (t: string) => t.replace(/\s+$/, "");
/** True when the console text is not (just) one of the problem's sample inputs. */
const isCustomInput = (p: ProblemDetail | null, text: string) =>
  !!p && norm(text) !== "" && !p.samples.some((s) => norm(s.input) === norm(text));
const cap = (d: string) => d[0] + d.slice(1).toLowerCase();
type LeftTab = "desc" | "hints" | "history" | "notes";

export default function ProblemPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const { items: catalog, ready } = useCatalog();
  const [stat, setStat] = useState<StaticProblem | null>(null);
  const [apiProblem, setApiProblem] = useState<ProblemDetail | null>(null);
  const [bookmarkOverride, setBookmarkOverride] = useState<boolean | null>(null);
  const [lang, setLang] = useState<Lang>("java");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [mode, setMode] = useState<"run" | "submit">("run");
  const [busy, setBusy] = useState<"" | "run" | "submit">("");
  const [elapsed, setElapsed] = useState(0);
  const [wait, setWait] = useState("");
  const [error, setError] = useState("");
  const [caseTab, setCaseTab] = useState(0);
  const [customInput, setCustomInput] = useState("");
  const [customRun, setCustomRun] = useState(false);
  const [theme, setTheme] = useState<ThemeName>("dark");
  const [leftPct, setLeftPct] = useState(45);
  const [editorPct, setEditorPct] = useState(60);
  const [drag, setDrag] = useState<"" | "v" | "h">("");
  const mainRef = useRef<HTMLDivElement>(null);
  const colRef = useRef<HTMLElement>(null);
  const [consoleTab, setConsoleTab] = useState<"testcase" | "result">("testcase");
  const [tab, setTab] = useState<LeftTab>("desc");
  const [view, setView] = useState<"desc" | "code">("desc");
  const [notes, setNotes] = useState("");
  const [fontSize, setFontSize] = useState(14);
  const [history, setHistory] = useState<Submission[]>([]);
  const [exec, setExec] = useState<ExecutionStatus | null>(null);
  const [hintsShown, setHintsShown] = useState(0);
  const [showApproach, setShowApproach] = useState(false);
  const [timer, setTimer] = useState({ on: false, secs: 0 });
  const [editorReady, setEditorReady] = useState(false);
  const [editorFailed, setEditorFailed] = useState(false);
  const [savedAt, setSavedAt] = useState(0);

  const meta = catalog.find((p) => p.slug === slug) ?? null;
  const problem: ProblemDetail | null = useMemo(() => {
    if (meta && stat) return { ...meta, ...stat };
    return apiProblem;
  }, [meta, stat, apiProblem]);
  const bookmarked = bookmarkOverride ?? problem?.bookmarked ?? false;

  const draftKey = (l: Lang) => `lc-draft:${slug}:${l}`;
  const loadHistory = useCallback(
    () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {}), [slug]);

  // Statement and starter code come from the bundled data, so they show instantly even while the backend sleeps.
  useEffect(() => {
    setStat(null); setApiProblem(null); setBookmarkOverride(null); setResult(null); setError("");
    setConsoleTab("testcase"); setTab("desc"); setView("desc"); setEditorReady(false); setEditorFailed(false);
    let alive = true;
    fetchStaticProblem(slug).then((s) => {
      if (!alive) return;
      if (s) setStat(s);
      else swr<ProblemDetail>(`/api/problems/${slug}`, (p) => alive && setApiProblem(p), () => {}).catch(() => {});
    });
    loadHistory();
    return () => { alive = false; };
  }, [slug, loadHistory]);

  useEffect(() => {
    const l = localStorage.getItem("lc-lang") as Lang | null;
    if (l && LANGS.some((x) => x.key === l)) setLang(l);
    const f = Number(localStorage.getItem("lc-font"));
    if (f >= 11 && f <= 24) setFontSize(f);
  }, []);
  useEffect(() => {
    try {
      const sv = JSON.parse(localStorage.getItem("lc-layout") ?? "null") as { leftPct?: number; editorPct?: number } | null;
      if (sv?.leftPct) setLeftPct(clamp(sv.leftPct, 22, 70));
      if (sv?.editorPct) setEditorPct(clamp(sv.editorPct, 25, 80));
    } catch { /* ignore corrupt layout */ }
    const sync = () => setTheme(currentTheme());
    sync(); window.addEventListener("lc-theme", sync);
    return () => window.removeEventListener("lc-theme", sync);
  }, []);
  useEffect(() => {
    try { localStorage.setItem("lc-layout", JSON.stringify({ leftPct, editorPct })); } catch { /* storage blocked */ }
  }, [leftPct, editorPct]);
  // Start the console on the first sample whenever a different problem is opened.
  useEffect(() => { setCustomInput(stat?.samples[0]?.input ?? apiProblem?.samples[0]?.input ?? ""); }, [stat, apiProblem]);
  useEffect(() => { setNotes(localStorage.getItem(`lc-notes:${slug}`) ?? ""); }, [slug]);
  useEffect(() => { setHintsShown(0); setShowApproach(false); setTimer({ on: false, secs: 0 }); }, [slug]);
  useEffect(() => {
    if (!timer.on) return;
    const t = setInterval(() => setTimer((x) => ({ ...x, secs: x.secs + 1 })), 1000);
    return () => clearInterval(t);
  }, [timer.on]);

  const starter = problem?.starterCode[lang];
  useEffect(() => {
    if (problem) setCode(localStorage.getItem(draftKey(lang)) ?? starter ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, lang, !!problem]);

  // If the code editor's CDN is blocked or slow, fall back to a plain text area so the user can still write code.
  useEffect(() => {
    if (view !== "code" && typeof window !== "undefined" && window.innerWidth <= 900) return;
    if (editorReady || editorFailed || !problem) return;
    const t = setTimeout(() => setEditorFailed(true), 12000);
    return () => clearTimeout(t);
  }, [editorReady, editorFailed, problem, view]);

  useEffect(() => {
    if (!busy) return;
    setElapsed(0);
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [busy]);

  const onChange = (v?: string) => {
    setCode(v ?? ""); localStorage.setItem(draftKey(lang), v ?? ""); setSavedAt(Date.now());
  };

  const run = useCallback(async (kind: "run" | "submit") => {
    if (busy) return;
    const custom = kind === "run" && isCustomInput(problem, customInput);
    setBusy(kind); setError(""); setMode(kind); setCustomRun(custom); setResult(null); setCaseTab(0); setConsoleTab("result"); setView("code"); setWait("");
    try {
      const st = await ensureAwake((n) => setWait(`Waking the server (free hosting sleeps when idle)… attempt ${n}`));
      setWait(""); setExec(st);
      if (!st.enabled || !st.reachable) throw new Error(`Code execution is unavailable: ${st.message}`);
      const r = await api<RunResponse>(`/api/problems/${slug}/${kind}`,
        { method: "POST", body: JSON.stringify({ language: lang, code, ...(custom ? { customInput } : {}) }) }, 120000);
      setResult(r);
      if (kind === "submit" && r.verdict === "ACCEPTED") recordAccepted();
      const firstFail = r.cases.findIndex((c) => !c.passed);
      setCaseTab(firstFail >= 0 ? firstFail : 0);
      if (kind === "submit") loadHistory();
    } catch (e) {
      setError((e as Error).message);
    } finally { setBusy(""); setWait(""); }
  }, [busy, slug, lang, code, problem, customInput, loadHistory]);

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
      await api(`/api/problems/${slug}/bookmark`, { method: bookmarked ? "DELETE" : "PUT" }, 90000);
      setBookmarkOverride(!bookmarked);
    } catch (e) { setError((e as Error).message); setConsoleTab("result"); }
  }

  /** Drag a divider: "v" resizes description/editor, "h" resizes editor/console. */
  function startDrag(kind: "v" | "h") {
    return (e: RPointerEvent) => {
      e.preventDefault(); setDrag(kind);
      const move = (ev: PointerEvent) => {
        if (kind === "v" && mainRef.current) {
          const r = mainRef.current.getBoundingClientRect();
          setLeftPct(clamp(((ev.clientX - r.left) / r.width) * 100, 22, 70));
        } else if (kind === "h" && colRef.current) {
          const r = colRef.current.getBoundingClientRect();
          setEditorPct(clamp(((ev.clientY - r.top) / r.height) * 100, 25, 80));
        }
      };
      const up = () => { window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); setDrag(""); };
      window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
    };
  }

  function reset() {
    if (!problem) return;
    localStorage.removeItem(draftKey(lang)); setCode(problem.starterCode[lang] ?? "");
  }

  if (!problem) {
    return (
      <div className="ws">
        <div className="ws-top"><Link className="back" href="/"><ListIcon /> Problem List</Link></div>
        <div style={{ padding: 24 }} className="mute">
          {ready && !meta && !apiProblem ? "Loading problem…" : "Loading problem…"}
        </div>
      </div>
    );
  }

  const study = STUDY[slug];
  const idx = catalog.findIndex((p) => p.slug === slug);
  const prev = idx > 0 ? catalog[idx - 1] : null;
  const next = idx >= 0 && idx + 1 < catalog.length ? catalog[idx + 1] : null;
  const clock = `${String(Math.floor(timer.secs / 60)).padStart(2, "0")}:${String(timer.secs % 60).padStart(2, "0")}`;
  const cur = result?.cases[caseTab];
  const custom = isCustomInput(problem, customInput);
  const sampleIdx = problem.samples.findIndex((x) => norm(x.input) === norm(customInput));
  const verdictText = customRun && result?.verdict === "ACCEPTED" ? "Finished" : title(result?.verdict ?? "");
  const monaco = LANGS.find((l) => l.key === lang)!.monaco;

  return (
    <div className={`ws view-${view}`}>
      <div className="ws-top">
        <div className="left">
          <Link className="back" href="/" title="Back to the problem list"><ListIcon /> <span className="hide-m">Problem List</span></Link>
          {prev ? <Link className="navbtn" href={`/problems/${prev.slug}`} title={`Previous: ${prev.title}`} aria-label="Previous problem"><ChevronLeft /></Link>
            : <span className="navbtn off"><ChevronLeft /></span>}
          {next ? <Link className="navbtn" href={`/problems/${next.slug}`} title={`Next: ${next.title}`} aria-label="Next problem"><ChevronRight /></Link>
            : <span className="navbtn off"><ChevronRight /></span>}
        </div>
        <div className="center">
          <button disabled={!!busy} onClick={() => run("run")} title="Ctrl/⌘ + '"><PlayIcon /> <span className="btn-label">{busy === "run" ? `Running… ${elapsed}s` : custom ? "Run custom" : "Run"}</span></button>
          <button className="primary" disabled={!!busy} onClick={() => run("submit")} title="Ctrl/⌘ + Enter">
            {busy === "submit" ? `Judging… ${elapsed}s` : "Submit"}
          </button>
        </div>
        <div className="right">
          <button className="ghost" onClick={() => setTimer((x) => ({ ...x, on: !x.on }))} title="Stopwatch for this attempt">
            ⏱ {clock}{timer.on ? " ⏸" : timer.secs ? " ▶" : ""}
          </button>
          <button className="ghost icon" onClick={toggleBookmark} title={bookmarked ? "Remove bookmark" : "Bookmark"} aria-label="Bookmark"
            style={{ color: bookmarked ? "var(--accent)" : undefined }}>{bookmarked ? "★" : "☆"}</button>
        </div>
      </div>

      <div className="seg" role="tablist">
        <button className={view === "desc" ? "on" : ""} onClick={() => setView("desc")}>Description</button>
        <button className={view === "code" ? "on" : ""} onClick={() => setView("code")}>Code</button>
      </div>

      <div ref={mainRef} className={`ws-main${drag ? ` dragging${drag === "h" ? " h" : ""}` : ""}`}
        style={{ ["--left" as string]: `${leftPct}%`, ["--edit" as string]: `${editorPct}%` }}>
        <section className="panel desc">
          <div className="panel-tabs">
            <button className={tab === "desc" ? "on" : ""} onClick={() => setTab("desc")}>Description</button>
            <button className={tab === "hints" ? "on" : ""} onClick={() => setTab("hints")}>Hints</button>
            <button className={tab === "history" ? "on" : ""} onClick={() => { setTab("history"); loadHistory(); }}>Submissions</button>
            <button className={tab === "notes" ? "on" : ""} onClick={() => setTab("notes")}>Notes{notes ? " •" : ""}</button>
          </div>
          <div className="panel-body">
            {tab === "desc" && (
              <>
                <h1 className="prob-title">{problem.id}. {problem.title}</h1>
                <div className="prob-meta">
                  <span className={`pill ${problem.difficulty}`}>{cap(problem.difficulty)}</span>
                  {problem.status === "SOLVED" && <span className="st"><StatusIcon status="SOLVED" /> Solved</span>}
                  {problem.acceptance != null && <span className="mute">Acceptance {problem.acceptance.toFixed(1)}%</span>}
                  {problem.tags.map((t) => <span className="tag" key={t}>{t}</span>)}
                </div>
                <div className="md"><Markdown>{problem.description}</Markdown></div>
              </>
            )}
            {tab === "hints" && (
              study ? (
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
              ) : <p className="mute">No hints for this problem yet.</p>
            )}
            {tab === "notes" && (
              <>
                <p className="mute" style={{ marginTop: 0 }}>Private notes for this problem, saved on this device.</p>
                <textarea className="notes" placeholder="Your approach, mistakes, edge cases to remember…" value={notes}
                  onChange={(e) => { setNotes(e.target.value); localStorage.setItem(`lc-notes:${slug}`, e.target.value); }} />
              </>
            )}
            {tab === "history" && (
              <table className="history">
                <thead><tr><th>Result</th><th>Lang</th><th>Tests</th><th>Time</th><th>When</th><th></th></tr></thead>
                <tbody>
                  {history.map((s) => (
                    <tr key={s.id}>
                      <td className={s.verdict}>{title(s.verdict)}</td><td>{s.language}</td>
                      <td>{s.passed}/{s.total}</td><td>{s.runtimeMs ?? "-"} ms</td>
                      <td className="mute">{new Date(s.createdAt).toLocaleString()}</td>
                      <td><button onClick={() => { setLang(s.language); setCode(s.code); setTab("desc"); setView("code"); }}>Load</button></td>
                    </tr>
                  ))}
                  {history.length === 0 && <tr><td colSpan={6} className="mute">No submissions yet (or the server is still waking up).</td></tr>}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <div className={`vdivider${drag === "v" ? " drag" : ""}`} role="separator" aria-orientation="vertical" title="Drag to resize" onPointerDown={startDrag("v")} />

        <section className="col2" ref={colRef}>
          <div className="panel editor-panel">
            <div className="editor-head">
              <CodeIcon />
              <select value={lang} aria-label="Language" onChange={(e) => { setLang(e.target.value as Lang); localStorage.setItem("lc-lang", e.target.value); }}>
                {LANGS.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
              </select>
              <span className="saved">{savedAt ? "Saved" : ""}</span>
              <span className="grow" />
              <select value={fontSize} title="Editor font size" aria-label="Font size" onChange={(e) => { setFontSize(Number(e.target.value)); localStorage.setItem("lc-font", e.target.value); }}>
                {[12, 14, 16, 18, 20].map((n) => <option key={n} value={n}>{n}px</option>)}
              </select>
              <button className="ghost" onClick={reset} title="Reset to starter code">Reset</button>
            </div>
            <div className="editor-wrap">
              {editorFailed ? (
                <textarea className="fallback-editor" spellCheck={false} value={code} aria-label="Code editor (plain text fallback)"
                  style={{ fontSize }} onChange={(e) => onChange(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Tab") {
                      e.preventDefault();
                      const t = e.currentTarget, s = t.selectionStart, en = t.selectionEnd;
                      onChange(t.value.slice(0, s) + "    " + t.value.slice(en));
                      requestAnimationFrame(() => { t.selectionStart = t.selectionEnd = s + 4; });
                    }
                  }} />
              ) : (
                <Editor height="100%" theme={theme === "light" ? "vs" : "vs-dark"} language={monaco} value={code} onChange={onChange}
                  onMount={() => setEditorReady(true)}
                  options={{ minimap: { enabled: false }, fontSize, automaticLayout: true, scrollBeyondLastLine: false, padding: { top: 8 } }} />
              )}
            </div>
          </div>

          <div className={`hdivider${drag === "h" ? " drag" : ""}`} role="separator" aria-orientation="horizontal" title="Drag to resize" onPointerDown={startDrag("h")} />
          <div className="panel console-panel">
            <div className="panel-tabs">
              <button className={consoleTab === "testcase" ? "on" : ""} onClick={() => setConsoleTab("testcase")}>Testcase</button>
              <button className={consoleTab === "result" ? "on" : ""} onClick={() => setConsoleTab("result")}>Test Result</button>
            </div>
            <div className="panel-body">
              {consoleTab === "testcase" && (
                <>
                  <div className="cases">
                    {problem.samples.map((x, i) => (
                      <button key={i} className={sampleIdx === i ? "on" : ""} onClick={() => setCustomInput(x.input)}>Case {i + 1}</button>
                    ))}
                    {custom && <span className="pill MEDIUM">Custom input</span>}
                  </div>
                  <div className="lbl">Input</div>
                  <textarea className="consoletext" spellCheck={false} value={customInput} aria-label="Test case input"
                    onChange={(e) => setCustomInput(e.target.value)} />
                  {sampleIdx >= 0 && problem.samples[sampleIdx] && (
                    <><div className="lbl">Expected output</div><pre className="io">{problem.samples[sampleIdx].expectedOutput}</pre></>
                  )}
                  <div className="hint-line">Run checks the sample cases. Edit the input to run your own test: custom runs print your output without a pass/fail check.</div>
                </>
              )}
              {consoleTab === "result" && (
                <>
                  {busy && (
                    <span className="mute">
                      {wait || (busy === "run" ? "Running your code on the sample cases" : "Judging against all test cases")}… {elapsed}s
                      {!wait && elapsed > 20 && " (the free judge can be slow — hang on)"}
                    </span>
                  )}
                  {error && !busy && <div className="banner err" style={{ margin: 0 }}>{error}</div>}
                  {exec && (!exec.enabled || !exec.reachable) && !busy && !error && <div className="banner warn">Code execution is unavailable: {exec.message}</div>}
                  {result && !busy && (
                    <>
                      <h3 className={`verdict ${result.verdict}`}>{verdictText}</h3>
                      <div className="mute" style={{ marginBottom: 10 }}>
                        {customRun ? "Custom input" : `${result.passed} / ${result.total} testcases passed${mode === "run" ? " · sample cases only" : ""}`}
                        {result.runtimeMs != null ? ` · Runtime: ${result.runtimeMs} ms` : ""}
                      </div>
                      {result.message && <div className={result.verdict === "ACCEPTED" ? "" : "err"}>{result.message}</div>}
                      {result.cases.length > 1 && (
                        <div className="cases" style={{ marginTop: 8 }}>
                          {result.cases.map((c, i) => (
                            <button key={i} className={caseTab === i ? "on" : ""} onClick={() => setCaseTab(i)}>
                              <span className={c.passed ? "ACCEPTED" : "WRONG_ANSWER"}><i className="dot" /></span>{c.sample ? `Case ${c.index}` : `Hidden ${c.index}`}
                            </button>
                          ))}
                        </div>
                      )}
                      {cur && (cur.input != null ? (
                        <>
                          <div className="lbl">Input</div><pre className="io">{cur.input}</pre>
                          <div className="lbl">Output</div><pre className="io">{cur.actual || "(empty)"}</pre>
                          {cur.expected != null && <><div className="lbl">Expected</div><pre className="io">{cur.expected}</pre></>}
                          {cur.error && <><div className="lbl">Error</div><pre className="io err">{cur.error}</pre></>}
                        </>
                      ) : (
                        <>
                          <div className="lbl">Hidden test case — details are not shown.</div>
                          {cur.error && <pre className="io err">{cur.error}</pre>}
                        </>
                      ))}
                    </>
                  )}
                  {!result && !busy && !error && !(exec && (!exec.enabled || !exec.reachable)) && (
                    <span className="mute">You must run your code first. Shortcuts: Ctrl/⌘+&apos; to run, Ctrl/⌘+Enter to submit.</span>
                  )}
                </>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
