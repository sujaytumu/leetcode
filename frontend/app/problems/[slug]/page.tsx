"use client";
import dynamic from "next/dynamic";
import { use, useEffect, useState } from "react";
import { api, Lang, ProblemDetail, RunResponse, Submission } from "@/lib/api";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });
const LANGS: { key: Lang; label: string; monaco: string }[] = [
  { key: "java", label: "Java", monaco: "java" }, { key: "python", label: "Python", monaco: "python" },
  { key: "javascript", label: "JavaScript", monaco: "javascript" }, { key: "cpp", label: "C++", monaco: "cpp" },
];

export default function ProblemPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [lang, setLang] = useState<Lang>("java");
  const [code, setCode] = useState("");
  const [result, setResult] = useState<RunResponse | null>(null);
  const [mode, setMode] = useState<"run" | "submit">("run");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"desc" | "history">("desc");
  const [history, setHistory] = useState<Submission[]>([]);

  const draftKey = (l: Lang) => `lc-draft:${slug}:${l}`;
  const loadHistory = () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {});

  useEffect(() => {
    api<ProblemDetail>(`/api/problems/${slug}`).then(setProblem).catch((e) => setError(e.message));
    loadHistory();
  }, [slug]);

  useEffect(() => {
    if (problem) setCode(localStorage.getItem(draftKey(lang)) ?? problem.starterCode[lang] ?? "");
  }, [problem, lang]);

  const onChange = (v?: string) => { setCode(v ?? ""); localStorage.setItem(draftKey(lang), v ?? ""); };

  async function exec(kind: "run" | "submit") {
    setBusy(true); setError(""); setMode(kind);
    try {
      setResult(await api<RunResponse>(`/api/problems/${slug}/${kind}`, {
        method: "POST", body: JSON.stringify({ language: lang, code }),
      }));
      if (kind === "submit") loadHistory();
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  async function toggleBookmark() {
    if (!problem) return;
    await api(`/api/problems/${slug}/bookmark`, { method: problem.bookmarked ? "DELETE" : "PUT" });
    setProblem({ ...problem, bookmarked: !problem.bookmarked });
  }

  function reset() {
    if (!problem) return;
    localStorage.removeItem(draftKey(lang)); setCode(problem.starterCode[lang] ?? "");
  }

  if (!problem) return <p className={error ? "err" : "mute"}>{error || "Loading…"}</p>;

  return (
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
            <p><span className={problem.difficulty}>{problem.difficulty}</span>{" "}
              {problem.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</p>
            <div className="desc">{problem.description}</div>
            {problem.samples.map((s, i) => (
              <div key={i}><b>Example {i + 1}</b>
                <pre>Input:  {s.input}{"\n"}Output: {s.expectedOutput}</pre></div>
            ))}
          </>
        ) : (
          <table style={{ marginTop: 12 }}>
            <thead><tr><th>Result</th><th>Lang</th><th>Tests</th><th>Time</th><th></th></tr></thead>
            <tbody>
              {history.map((s) => (
                <tr key={s.id}>
                  <td className={s.verdict}>{s.verdict.replaceAll("_", " ")}</td><td>{s.language}</td>
                  <td>{s.passed}/{s.total}</td><td>{s.runtimeMs ?? "-"} ms</td>
                  <td><button onClick={() => { setLang(s.language); setCode(s.code); setTab("desc"); }}>Load</button></td>
                </tr>
              ))}
              {history.length === 0 && <tr><td colSpan={5} className="mute">No submissions yet.</td></tr>}
            </tbody>
          </table>
        )}
      </section>
      <section className="col">
        <div className="bar">
          <select value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
            {LANGS.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
          </select>
          <button onClick={reset}>Reset</button><span className="grow" />
          <button disabled={busy} onClick={() => exec("run")}>Run</button>
          <button className="primary" disabled={busy} onClick={() => exec("submit")}>Submit</button>
        </div>
        <div className="pane" style={{ padding: 0, flex: 3 }}>
          <Editor height="100%" theme="vs-dark" language={LANGS.find((l) => l.key === lang)!.monaco}
            value={code} onChange={onChange} options={{ minimap: { enabled: false }, fontSize: 14, automaticLayout: true }} />
        </div>
        <div className="pane" style={{ flex: 2 }}>
          {busy && <span className="mute">Running…</span>}
          {error && <p className="err">{error}</p>}
          {result && !busy && (
            <>
              <h3 className={result.verdict}>{result.verdict.replaceAll("_", " ")}
                <span className="mute"> · {result.passed}/{result.total} passed{result.runtimeMs != null ? ` · ${result.runtimeMs} ms` : ""} ({mode})</span></h3>
              {result.message && <pre>{result.message}</pre>}
              {result.cases.map((c) => (
                <div key={c.index}>
                  <b className={c.passed ? "ACCEPTED" : "WRONG_ANSWER"}>{c.sample ? `Sample ${c.index + 1}` : `Case ${c.index + 1}`}: {c.passed ? "passed" : c.verdict.replaceAll("_", " ")}</b>
                  {c.input != null && <pre>Input:    {c.input}{"\n"}Expected: {c.expected}{"\n"}Actual:   {c.actual ?? ""}{c.error ? `\n${c.error}` : ""}</pre>}
                </div>
              ))}
            </>
          )}
          {!result && !busy && !error && <span className="mute">Run or submit to see results.</span>}
        </div>
      </section>
    </div>
  );
}
