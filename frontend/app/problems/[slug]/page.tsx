"use client";
import dynamic from "next/dynamic";
import Markdown from "react-markdown";
import { type ComponentType, type PointerEvent as RPointerEvent, use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  Answer, api, ApiError, ExecutionStatus, Lang, ProblemDetail, ProblemSummary, RunResponse,
  Study, Submission,
} from "@/lib/api";
import { loadAll, swr } from "@/lib/local";
import { useMeta } from "@/lib/meta";
import EditorSettingsModal from "@/components/EditorSettingsModal";
import VoteButtons from "@/components/VoteButtons";
import { monacoTheme, useEditorSettings } from "@/lib/editorSettings";
import Skeleton from "@/components/Skeleton";
import SimilarProblems from "@/components/SimilarProblems";
import SubmissionStatsPanel, { fmtMem } from "@/components/SubmissionStatsPanel";
import FreeSpace from "@/components/FreeSpace";
import { composeProgram, extractUser, type Parts, shiftErrorLines, splitTemplate } from "@/lib/harness";
import { currentTheme, type ThemeName } from "@/components/ThemeToggle";

import type { EditorProps } from "@monaco-editor/react";
// Without this, next/dynamic infers ComponentType<never> for Monaco's Editor and the production build fails type-checking.
const Editor = dynamic<EditorProps>(
  () => import("@monaco-editor/react").then((m) => m.default as unknown as ComponentType<EditorProps>), {
  ssr: false, loading: () => <p className="mute" style={{ padding: 16 }}>Loading editor…</p>,
});
const ANSWER_ORDER = ["cpp", "java", "python", "javascript"];
const LANG_LABEL: Record<string, string> = { cpp: "C++", java: "Java", python: "Python", javascript: "JavaScript" };
type AnswerState = { status: "idle" | "loading" | "ready" | "none" | "error"; data?: Answer; error?: string };
const title = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));
const answerKeys = (a: Answer) =>
  ANSWER_ORDER.filter((k) => k in a.solutions).concat(Object.keys(a.solutions).filter((k) => !ANSWER_ORDER.includes(k)));
const norm = (t: string) => t.replace(/\s+$/, "");
/** True when the console text is not (just) one of the problem's sample inputs. */
const isCustomInput = (p: ProblemDetail | null, text: string) =>
  !!p && norm(text) !== "" && !p.samples.some((s) => norm(s.input) === norm(text));

export default function ProblemPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loadError, setLoadError] = useState("");
  const meta = useMeta();
  const [lang, setLang] = useState<Lang>("");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [mode, setMode] = useState<"run" | "submit">("run");
  const [customRun, setCustomRun] = useState(false);
  const [busy, setBusy] = useState<"" | "run" | "submit">("");
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const [caseTab, setCaseTab] = useState(0);
  const [tab, setTab] = useState<"desc" | "editorial" | "answer" | "history" | "notes">("desc");
  const [consoleTab, setConsoleTab] = useState<"case" | "result">("case");
  const [customInput, setCustomInput] = useState("");
  const [notes, setNotes] = useState("");
  const [ed, setEd, resetEd] = useEditorSettings();
  const fontSize = ed.fontSize;
  const [showSettings, setShowSettings] = useState(false);
  const [history, setHistory] = useState<Submission[]>([]);
  const [openSub, setOpenSub] = useState<Submission | null>(null);
  const [exec, setExec] = useState<ExecutionStatus | null>(null);
  const [all, setAll] = useState<ProblemSummary[]>([]);
  const [hintsShown, setHintsShown] = useState(0);
  const [showApproach, setShowApproach] = useState(false);
  const [timer, setTimer] = useState({ on: false, secs: 0 });
  const [theme, setTheme] = useState<ThemeName>("dark");
  const [leftPct, setLeftPct] = useState(42);
  const [editorPct, setEditorPct] = useState(60);
  const [drag, setDrag] = useState<"" | "v" | "h">("");
  const [study, setStudy] = useState<Study | null>(null);
  const [focus, setFocus] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showKeys, setShowKeys] = useState(false);
  const [answer, setAnswer] = useState<AnswerState>({ status: "idle" });
  const [answerLang, setAnswerLang] = useState("");
  const [runParts, setRunParts] = useState<Parts | null>(null);
  const pendingRef = useRef<{ lang: string; code: string } | null>(null);
  const slugRef = useRef(slug);
  slugRef.current = slug;
  const workspaceRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLElement>(null);

  // The editor shows only the user's part; the judge gets the full program (hidden shell + user code).
  const parts = useMemo(
    () => (problem && lang ? splitTemplate(problem.starterCode[lang] ?? "", lang) : null), [problem, lang]);
  const draftKey = (l: Lang) => `lc-draft2:${slug}:${l}`;
  const loadHistory = useCallback(
    () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {}), [slug]);
  const checkExec = useCallback(
    () => api<ExecutionStatus>("/api/execution/status", {}, 20000).then(setExec)
      .catch((e: ApiError) => setExec({ enabled: true, reachable: false, provider: "unknown", message: e.message })), []);

  const loadProblem = useCallback(() => {
    setLoadError("");
    swr<ProblemDetail>(`/api/problems/${slug}`, (p) => setProblem(p), () => {})
      .catch((e) => setLoadError(e.message));
  }, [slug]);

  useEffect(() => { loadProblem(); loadHistory(); checkExec(); }, [loadProblem, loadHistory, checkExec]);
  useEffect(() => {
    if (!meta || lang) return;
    const saved = localStorage.getItem("lc-lang");
    setLang(saved && meta.languages.some((x) => x.key === saved) ? saved : meta.defaultLanguage);
  }, [meta, lang]);
  useEffect(() => {
    let live = true;
    setStudy(null);
    api<Study | undefined>(`/api/problems/${slug}/study`)
      .then((s) => { if (live) setStudy(s ?? null); })
      .catch(() => { if (live) setStudy(null); });
    return () => { live = false; };
  }, [slug]);
  const hasProblem = problem !== null;
  useEffect(() => { if (hasProblem) loadAll((items) => setAll(items), () => {}).catch(() => {}); }, [hasProblem]);
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("lc-layout") ?? "null") as { leftPct?: number; editorPct?: number } | null;
      if (saved?.leftPct) setLeftPct(clamp(saved.leftPct, 22, 70));
      if (saved?.editorPct) setEditorPct(clamp(saved.editorPct, 25, 80));
    } catch { /* ignore corrupt layout */ }
  }, []);
  useEffect(() => {
    try { localStorage.setItem("lc-layout", JSON.stringify({ leftPct, editorPct })); } catch { /* storage blocked */ }
  }, [leftPct, editorPct]);
  useEffect(() => {
    const sync = () => setTheme(currentTheme());
    sync();
    window.addEventListener("lc-theme", sync);
    return () => window.removeEventListener("lc-theme", sync);
  }, []);
  useEffect(() => { setNotes(localStorage.getItem(`lc-notes:${slug}`) ?? ""); }, [slug]);
  useEffect(() => { setAnswer({ status: "idle" }); setAnswerLang(""); }, [slug]);
  useEffect(() => { setHintsShown(0); setShowApproach(false); setTimer({ on: false, secs: 0 }); }, [slug]);
  // Start the console on the first sample whenever a different problem is opened.
  useEffect(() => {
    if (problem) { setCustomInput(problem.samples[0]?.input ?? ""); setResult(null); setConsoleTab("case"); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problem?.slug]);
  useEffect(() => {
    if (!timer.on) return;
    const t = setInterval(() => setTimer((x) => ({ ...x, secs: x.secs + 1 })), 1000);
    return () => clearInterval(t);
  }, [timer.on]);

  useEffect(() => {
    if (!problem || !lang) return;
    const pending = pendingRef.current;
    if (pending && pending.lang === lang) {
      pendingRef.current = null;
      setCode(pending.code);
      localStorage.setItem(draftKey(lang), pending.code);
      return;
    }
    const initial = parts ? parts.stub : problem.starterCode[lang] ?? "";
    setCode(localStorage.getItem(draftKey(lang)) ?? initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problem, lang, parts]);

  useEffect(() => {
    if (!busy) return;
    setElapsed(0);
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [busy]);

  const onChange = (v?: string) => { setCode(v ?? ""); localStorage.setItem(draftKey(lang), v ?? ""); };

  const run = useCallback(async (kind: "run" | "submit") => {
    if (busy) return;
    const custom = kind === "run" && isCustomInput(problem, customInput);
    setBusy(kind); setError(""); setMode(kind); setCustomRun(custom); setResult(null); setCaseTab(0);
    setConsoleTab("result");
    setRunParts(parts);
    try {
      const source = parts ? composeProgram(parts, code) : code;
      const r = await api<RunResponse>(`/api/problems/${slug}/${kind}`,
        { method: "POST", body: JSON.stringify({ language: lang, code: source, ...(custom ? { customInput } : {}) }) }, 120000);
      setResult(r);
      const firstFail = r.cases.findIndex((c) => !c.passed);
      setCaseTab(firstFail >= 0 ? firstFail : 0);
      if (kind === "submit") loadHistory();
      checkExec();
    } catch (e) {
      setError((e as Error).message);
      checkExec();
    } finally { setBusy(""); }
  }, [busy, slug, lang, code, parts, problem, customInput, loadHistory, checkExec]);

  const runRef = useRef(run);
  runRef.current = run;
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "'") { e.preventDefault(); runRef.current("run"); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runRef.current("submit"); }
      if (e.key === "Escape") { setShowKeys(false); setShowSettings(false); setFocus(false); }
      const el = e.target as HTMLElement | null;
      const typing = !!el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT" || el.isContentEditable);
      if (e.key === "?" && !typing && !e.ctrlKey && !e.metaKey) setShowKeys((v) => !v);
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

  async function copyCode() {
    try { await navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 1500); }
    catch { setError("Could not copy: clipboard access was blocked by the browser."); }
  }

  function reset() {
    if (!problem) return;
    localStorage.removeItem(draftKey(lang)); setCode(parts ? parts.stub : problem.starterCode[lang] ?? "");
  }

  function loadSubmission(s: Submission) {
    const user = extractUser(s.code, s.language) ?? splitTemplate(s.code, s.language)?.stub ?? null;
    if (user === null) {
      setError("This older submission was saved as a full program and can't be opened in the simplified editor.");
      setConsoleTab("result");
      return;
    }
    if (s.language === lang) { setCode(user); localStorage.setItem(draftKey(lang), user); }
    else { pendingRef.current = { lang: s.language, code: user }; setLang(s.language); }
    setTab("desc");
  }

  async function revealAnswer() {
    const forSlug = slug;
    setAnswer({ status: "loading" });
    try {
      const a = await api<Answer | undefined>(`/api/problems/${forSlug}/solution`, {}, 30000);
      if (slugRef.current !== forSlug) return;
      if (!a) { setAnswer({ status: "none" }); return; }
      const keys = answerKeys(a);
      setAnswerLang(keys.includes(lang) ? lang : keys[0]);
      setAnswer({ status: "ready", data: a });
    } catch (e) {
      if (slugRef.current === forSlug) setAnswer({ status: "error", error: (e as Error).message });
    }
  }

  async function copyAnswer(text: string) {
    try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }
    catch { setError("Could not copy: clipboard access was blocked by the browser."); }
  }

  /** Drag a divider: "v" resizes description/editor, "h" resizes editor/console. */
  function startDrag(kind: "v" | "h") {
    return (e: RPointerEvent) => {
      e.preventDefault();
      setDrag(kind);
      const move = (ev: PointerEvent) => {
        if (kind === "v" && workspaceRef.current) {
          const r = workspaceRef.current.getBoundingClientRect();
          setLeftPct(clamp(((ev.clientX - r.left) / r.width) * 100, 22, 70));
        } else if (kind === "h" && rightRef.current) {
          const r = rightRef.current.getBoundingClientRect();
          const barH = (rightRef.current.firstElementChild as HTMLElement | null)?.offsetHeight ?? 0;
          setEditorPct(clamp(((ev.clientY - r.top - barH - 8) / r.height) * 100, 25, 80));
        }
      };
      const up = () => {
        window.removeEventListener("pointermove", move);
        window.removeEventListener("pointerup", up);
        setDrag("");
      };
      window.addEventListener("pointermove", move);
      window.addEventListener("pointerup", up);
    };
  }

  if (!problem) {
    return <FreeSpace loading={!loadError} error={loadError} onRetry={loadProblem} label="Loading problem…" />;
  }

  // Offer the languages the backend supports for this problem (those it has starter code for).
  const supported = meta?.languages.filter((l) => l.key in problem.starterCode) ?? [];
  const languages = supported.length ? supported : (meta?.languages ?? []);
  const execDown = exec && (!exec.enabled || !exec.reachable);
  const idx = all.findIndex((p) => p.slug === slug);
  const prev = idx > 0 ? all[idx - 1] : null;
  const next = idx >= 0 && idx + 1 < all.length ? all[idx + 1] : null;
  const clock = `${String(Math.floor(timer.secs / 60)).padStart(2, "0")}:${String(timer.secs % 60).padStart(2, "0")}`;
  const cur = result?.cases[caseTab];
  const fix = (t: string) => (runParts ? shiftErrorLines(t, runParts) : t);
  const custom = isCustomInput(problem, customInput);
  const sampleIdx = problem.samples.findIndex((s) => norm(s.input) === norm(customInput));
  const verdictText = customRun && result?.verdict === "ACCEPTED" ? "Finished" : title(result?.verdict ?? "");

  return (
    <>
      {execDown && (
        <div className="banner warn">
          Code execution is unavailable: {exec.message} Run and Submit will show an error until it is back.
          <button onClick={checkExec}>Re-check</button>
        </div>
      )}
      <div ref={workspaceRef} className={`workspace${drag ? " dragging" : ""}${focus ? " focus" : ""}`}
        style={{ gridTemplateColumns: focus ? "minmax(0, 1fr)" : `${leftPct}% 8px minmax(0, 1fr)` }}>
        <section className="pane left" hidden={focus}>
          <div className="lctabs">
            <button className={tab === "desc" ? "on" : ""} onClick={() => setTab("desc")}>Description</button>
            <button className={tab === "editorial" ? "on" : ""} onClick={() => setTab("editorial")}>Editorial</button>
            <button className={tab === "answer" ? "on" : ""} onClick={() => setTab("answer")}>Answer</button>
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
          <div className="left-body">
            {tab === "desc" ? (
              <>
                <div className="titlerow">
                  <h2 className="ptitle">{problem.number ?? problem.id}. {problem.title}</h2>
                  {problem.status === "SOLVED" && <span className="solved">Solved ✓</span>}
                </div>
                <div className="pmeta">
                  <span className={`pill ${problem.difficulty}`}>{title(problem.difficulty)}</span>
                  {problem.acceptance != null && <span className="mute">Acceptance {problem.acceptance.toFixed(1)}%</span>}
                  <VoteButtons slug={slug} />
                </div>
                <div className="pmeta">{problem.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</div>
                <div className="md"><Markdown>{problem.description}</Markdown></div>
                <SimilarProblems current={problem} all={all} />
              </>
            ) : tab === "editorial" ? (
              <div className="editorial">
                {study ? (
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
                ) : <p className="mute">No editorial for this problem yet.</p>}
              </div>
            ) : tab === "answer" ? (
              <div className="answer">
                {answer.status === "idle" && (
                  <>
                    <p className="mute">Spoiler: try it yourself first. The Editorial tab has hints that do not give it away.</p>
                    <button className="primary" onClick={revealAnswer}>Show answer</button>
                  </>
                )}
                {answer.status === "loading" && <FreeSpace loading compact label="Loading answer…" />}
                {answer.status === "none" && <p className="mute">No answer has been published for this problem yet. They are added in batches.</p>}
                {answer.status === "error" && <div className="banner err">{answer.error} <button onClick={revealAnswer}>Retry</button></div>}
                {answer.status === "ready" && answer.data && (
                  <>
                    <div className="casechips">
                      {answerKeys(answer.data).map((k) => (
                        <button key={k} className={answerLang === k ? "on" : ""} onClick={() => setAnswerLang(k)}>
                          {languages.find((l) => l.key === k)?.label ?? LANG_LABEL[k] ?? k}
                        </button>
                      ))}
                      <span className="grow" />
                      <button onClick={() => copyAnswer(answer.data!.solutions[answerLang] ?? "")}>{copied ? "✔ Copied" : "Copy"}</button>
                    </div>
                    <pre className="answer-code">{answer.data.solutions[answerLang]}</pre>
                    {answer.data.editorial && <div className="md"><Markdown>{answer.data.editorial}</Markdown></div>}
                  </>
                )}
              </div>
            ) : tab === "notes" ? (
              <>
                <p className="mute" style={{ marginBottom: 6 }}>Private notes for this problem, saved on this device.</p>
                <textarea className="notes" placeholder="Your approach, mistakes, edge cases to remember…" value={notes}
                  onChange={(e) => { setNotes(e.target.value); localStorage.setItem(`lc-notes:${slug}`, e.target.value); }} />
              </>
            ) : (
              openSub ? (
                <div className="subdetail">
                  <button className="ghost" onClick={() => setOpenSub(null)}>← All submissions</button>
                  <h3 className={`verdict ${openSub.verdict}`} style={{ marginTop: 10 }}>{title(openSub.verdict)}</h3>
                  <div className="vstats">
                    {openSub.passed} / {openSub.total} testcases passed · {openSub.language} · {new Date(openSub.createdAt).toLocaleString()}
                  </div>
                  {openSub.verdict === "ACCEPTED" && <SubmissionStatsPanel id={openSub.id} />}
                  <div className="iolabel" style={{ marginTop: 14 }}>Code</div>
                  <pre className="subcode">{openSub.code}</pre>
                  <button onClick={() => { setLang(openSub.language); setCode(openSub.code); setTab("desc"); setOpenSub(null); }}>Load into editor</button>
                </div>
              ) : (
              <table>
                <thead><tr><th>Status</th><th>Language</th><th>Runtime</th><th>Memory</th><th>Submitted</th><th></th></tr></thead>
                <tbody>
                  {history.map((s) => (
                    <tr key={s.id} className="subrow" onClick={() => setOpenSub(s)} title="Open details">
                      <td className={s.verdict}><b>{title(s.verdict)}</b><div className="mute" style={{ fontSize: 12 }}>{s.passed}/{s.total} passed</div></td><td>{s.language}</td>
                      <td>{s.runtimeMs != null ? `${s.runtimeMs} ms` : "N/A"}</td><td>{s.memoryKb != null ? fmtMem(s.memoryKb) : "N/A"}</td>
                      <td className="mute">{new Date(s.createdAt).toLocaleString()}</td>
                      <td><button onClick={(e) => { e.stopPropagation(); loadSubmission(s); }}>Load</button></td>
                    </tr>
                  ))}
                  {history.length === 0 && <tr><td colSpan={6} className="mute">No submissions yet.</td></tr>}
                </tbody>
              </table>
              )
            )}
          </div>
        </section>

        <div hidden={focus} className={`vdivider${drag === "v" ? " drag" : ""}`} role="separator" aria-orientation="vertical"
          title="Drag to resize" onPointerDown={startDrag("v")} />

        <section className="right" ref={rightRef}>
          <div className="bar actionbar" style={{ marginBottom: 8 }}>
            <select value={lang} onChange={(e) => { setLang(e.target.value); localStorage.setItem("lc-lang", e.target.value); }}>
              {languages.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
            </select>
            <select value={fontSize} title="Editor font size" onChange={(e) => setEd({ fontSize: Number(e.target.value) })}>
              {[12, 14, 16, 18, 20].map((n) => <option key={n} value={n}>{n}px</option>)}
            </select>
            <button onClick={reset} title="Reset to starter code">Reset</button>
            <button onClick={copyCode} title="Copy your code">{copied ? "✔ Copied" : "Copy"}</button>
            <button onClick={() => setFocus((f) => !f)} title="Hide the description and focus on the editor (Esc to exit)">
              {focus ? "⤡ Exit focus" : "⤢ Focus"}
            </button>
            <button onClick={() => setShowSettings(true)} title="Editor settings" aria-label="Editor settings">⚙</button>
            <button onClick={() => setShowKeys(true)} title="Keyboard shortcuts (?)" aria-label="Keyboard shortcuts">⌨</button>
            <span className="grow" />
            <button disabled={!!busy} onClick={() => run("run")} title="Ctrl/⌘ + '">
              {busy === "run" ? `Running… ${elapsed}s` : custom ? "▶ Run custom" : "▶ Run"}
            </button>
            <button className="primary" disabled={!!busy} onClick={() => run("submit")} title="Ctrl/⌘ + Enter">
              {busy === "submit" ? `Judging… ${elapsed}s` : "Submit"}
            </button>
          </div>
          <div className="pane editor-wrap" style={{ flex: `0 0 ${editorPct}%` }}>
            <Editor height="100%" theme={monacoTheme(ed.editorTheme, theme)}
              language={languages.find((l) => l.key === lang)?.editorMode ?? "plaintext"}
              value={code} onChange={onChange}
              options={{
                minimap: { enabled: ed.minimap }, fontSize, tabSize: ed.tabSize, insertSpaces: true,
                wordWrap: ed.wordWrap ? "on" : "off", lineNumbers: ed.lineNumbers ? "on" : "off",
                automaticLayout: true, scrollBeyondLastLine: false,
              }} />
          </div>
          <div className={`hdivider${drag === "h" ? " drag" : ""}`} role="separator" aria-orientation="horizontal"
            title="Drag to resize" onPointerDown={startDrag("h")} />
          <div className="pane console result-pane">
            <div className="lctabs">
              <button className={consoleTab === "case" ? "on" : ""} onClick={() => setConsoleTab("case")}>Testcase</button>
              <button className={consoleTab === "result" ? "on" : ""} onClick={() => setConsoleTab("result")}>
                Test Result{result && !busy ? <span className={result.verdict === "ACCEPTED" ? "ACCEPTED" : "WRONG_ANSWER"}> ●</span> : null}
              </button>
            </div>
            <div className="body">
              {consoleTab === "case" ? (
                <>
                  <div className="casechips">
                    {problem.samples.map((s, i) => (
                      <button key={i} className={sampleIdx === i ? "on" : ""} onClick={() => setCustomInput(s.input)}>Case {i + 1}</button>
                    ))}
                    {custom && <span className="pill MEDIUM">Custom input</span>}
                  </div>
                  <div className="iolabel">Input</div>
                  <textarea className="consoletext" spellCheck={false} value={customInput}
                    onChange={(e) => setCustomInput(e.target.value)} aria-label="Test case input" />
                  {sampleIdx >= 0 && problem.samples[sampleIdx] && (
                    <>
                      <div className="iolabel">Expected output</div>
                      <pre>{problem.samples[sampleIdx].expectedOutput}</pre>
                    </>
                  )}
                  <div className="hint-line">
                    Run checks the sample cases. Edit the input to run your own test: custom runs print your output without a pass/fail check.
                  </div>
                </>
              ) : (
                <>
                  {busy && (
                    <span className="mute">
                      {busy === "run" ? (custom ? "Running your code on the custom input" : "Running your code on the sample cases") : "Judging against all test cases"}… {elapsed}s
                      {elapsed > 20 && " (the free judge can be slow — hang on)"}
                    </span>
                  )}
                  {error && !busy && <div className="banner err" style={{ margin: 0 }}>{error}</div>}
                  {result && !busy && (
                    <>
                      <h3 className={`verdict ${result.verdict}`}>{verdictText}</h3>
                      <div className="vstats">
                        {customRun
                          ? "Custom input"
                          : `${result.passed} / ${result.total} testcases passed${mode === "run" ? " · sample cases only" : ""}`}
                        {result.runtimeMs != null ? ` · Runtime: ${result.runtimeMs} ms` : ""}{result.memoryKb != null ? ` · Memory: ${fmtMem(result.memoryKb)}` : ""}
                      </div>
                      {mode === "submit" && result.verdict === "ACCEPTED" && result.submissionId != null && <SubmissionStatsPanel id={result.submissionId} />}
                      {result.message && <div className={result.verdict === "ACCEPTED" ? "" : "err"}>{fix(result.message)}</div>}
                      {result.cases.length > 1 && (
                        <div className="casechips" style={{ marginTop: 8 }}>
                          {result.cases.map((c, i) => (
                            <button key={i} className={caseTab === i ? "on" : ""} onClick={() => setCaseTab(i)}>
                              <span className={c.passed ? "ACCEPTED" : "WRONG_ANSWER"}>●</span> {c.sample ? `Case ${c.index}` : `Hidden ${c.index}`}
                            </button>
                          ))}
                        </div>
                      )}
                      {cur && (cur.input != null ? (
                        <>
                          <div className="iolabel">Input</div><pre>{cur.input}</pre>
                          <div className="iolabel">Output</div><pre>{cur.actual || "(empty)"}</pre>
                          {cur.expected != null && <><div className="iolabel">Expected</div><pre>{cur.expected}</pre></>}
                          {cur.error && <><div className="iolabel">Error</div><pre className="err">{fix(cur.error)}</pre></>}
                        </>
                      ) : (
                        <>
                          <div className="mute">Hidden test case — details are not shown.</div>
                          {cur.error && <pre className="err">{fix(cur.error)}</pre>}
                        </>
                      ))}
                    </>
                  )}
                  {!result && !busy && !error && <span className="mute">Run or submit to see results. Shortcuts: Ctrl/⌘+' to run, Ctrl/⌘+Enter to submit.</span>}
                </>
              )}
            </div>
          </div>
        </section>
      </div>
      {showSettings && <EditorSettingsModal settings={ed} onChange={setEd} onReset={resetEd} onClose={() => setShowSettings(false)} />}
      {showKeys && (
        <div className="modal-back" onClick={() => setShowKeys(false)}>
          <div className="modal" role="dialog" aria-label="Keyboard shortcuts" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Keyboard shortcuts</h3>
            <table>
              <tbody>
                <tr><td><kbd>Ctrl/⌘</kbd> + <kbd>&apos;</kbd></td><td>Run on the console input</td></tr>
                <tr><td><kbd>Ctrl/⌘</kbd> + <kbd>Enter</kbd></td><td>Submit</td></tr>
                <tr><td><kbd>?</kbd></td><td>Show or hide this help</td></tr>
                <tr><td><kbd>Esc</kbd></td><td>Close help / leave focus mode</td></tr>
              </tbody>
            </table>
            <p className="mute" style={{ marginBottom: 0 }}>Drag the dividers to resize the panes; the layout is remembered.</p>
            <div style={{ textAlign: "right", marginTop: 10 }}><button onClick={() => setShowKeys(false)}>Close</button></div>
          </div>
        </div>
      )}
    </>
  );
}
