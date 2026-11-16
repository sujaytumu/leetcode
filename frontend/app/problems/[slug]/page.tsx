"use client";
import dynamic from "next/dynamic";
import Markdown from "react-markdown";
import { use, useCallback, useEffect, useRef, useState } from "react";
import {
  api, apiWithWake, ApiError, ExecutionStatus, Lang, ProblemDetail, RunResponse, Submission,
} from "@/lib/api";

const Editor = dynamic(() => import("@monaco-editor/react"), {
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
  const [tab, setTab] = useState<"desc" | "history">("desc");
  const [history, setHistory] = useState<Submission[]>([]);
  const [exec, setExec] = useState<ExecutionStatus | null>(null);

  const draftKey = (l: Lang) => `lc-draft:${slug}:${l}`;
  const loadHistory = useCallback(
    () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {}), [slug]);
  const checkExec = useCallback(
    () => api<ExecutionStatus>("/api/execution/status", {}, 20000).then(setExec)
      .catch((e: ApiError) => setExec({ enabled: true, reachable: false, provider: "unknown", message: e.message })), []);

  const loadProblem = useCallback(() => {
    setLoadError("");
    apiWithWake<ProblemDetail>(`/api/problems/${slug}`, () => setWaking(true))
      .then((p) => { setProblem(p); setWaking(false); })
      .catch((e) => { setLoadError(e.message); setWaking(false); });
  }, [slug]);

  useEffect(() => { loadProblem(); loadHistory(); checkExec(); }, [loadProblem, loadHistory, checkExec]);

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
  const cur = result?.cases[caseTab];

  return (
    <>
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
            <span className="grow" />
            <button onClick={toggleBookmark}>{problem.bookmarked ? "★ Bookmarked" : "☆ Bookmark"}</button>
          </div>
          {tab === "desc" ? (
            <>
              <h2>{problem.id}. {problem.title}</h2>
              <p><span className={problem.difficulty}>{title(problem.difficulty)}</span>{" "}
                {problem.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</p>
              <div className="md"><Markdown>{problem.description}</Markdown></div>
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
          <div className="bar">
            <select value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
              {LANGS.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
            </select>
            <button onClick={reset} title="Reset to starter code">Reset</button><span className="grow" />
            <button disabled={!!busy} onClick={() => run("run")} title="Ctrl/⌘ + '">
              {busy === "run" ? `Running… ${elapsed}s` : "▶ Run"}
            </button>
            <button className="primary" disabled={!!busy} onClick={() => run("submit")} title="Ctrl/⌘ + Enter">
              {busy === "submit" ? `Judging… ${elapsed}s` : "Submit"}
            </button>
          </div>
          <div className="pane" style={{ padding: 0, flex: 3 }}>
            <Editor height="100%" theme="vs-dark" language={LANGS.find((l) => l.key === lang)!.monaco}
              value={code} onChange={onChange}
              options={{ minimap: { enabled: false }, fontSize: 14, automaticLayout: true, scrollBeyondLastLine: false }} />
          </div>
          <div className="pane" style={{ flex: 2 }}>
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
