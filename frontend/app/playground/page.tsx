"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import dynamic from "next/dynamic";
import { type ComponentType, useCallback, useEffect, useRef, useState } from "react";
import type { EditorProps } from "@monaco-editor/react";
import { api } from "@/lib/api";
import { useMeta } from "@/lib/meta";
import { monacoTheme, useEditorSettings } from "@/lib/editorSettings";
import { currentTheme, type ThemeName } from "@/components/ThemeToggle";

// Same typing workaround as the problem page: without it next/dynamic infers ComponentType<never>.
const Editor = dynamic<EditorProps>(
  () => import("@monaco-editor/react").then((m) => m.default as unknown as ComponentType<EditorProps>), {
  ssr: false, loading: () => <p className="mute" style={{ padding: 16 }}>Loading editor…</p>,
});

interface RunResult { status: string; stdout: string; stderr: string; compileOutput: string; timeMs: number | null; memoryKb: number | null }

const HELLO: Record<string, string> = {
  python: 'name = input()\nprint(f"Hello, {name}!")\n',
  javascript: 'const name = require("fs").readFileSync(0, "utf8").trim();\nconsole.log(`Hello, ${name}!`);\n',
  java: 'import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner in = new Scanner(System.in);\n        String name = in.hasNextLine() ? in.nextLine() : "world";\n        System.out.println("Hello, " + name + "!");\n    }\n}\n',
  cpp: '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    string name;\n    getline(cin, name);\n    cout << "Hello, " << name << "!" << endl;\n    return 0;\n}\n',
};
const STATUS_TEXT: Record<string, string> = {
  OK: "Finished", COMPILE_ERROR: "Compilation Error", RUNTIME_ERROR: "Runtime Error",
  TIME_LIMIT_EXCEEDED: "Time Limit Exceeded", INTERNAL_ERROR: "Judge Error",
};

const safeGet = (k: string) => { try { return localStorage.getItem(k); } catch { return null; } };
const safeSet = (k: string, v: string) => { try { localStorage.setItem(k, v); } catch { /* storage blocked */ } };

export default function Playground() {
  usePageTitle("Playground");
  const meta = useMeta();
  const [ed] = useEditorSettings();
  const [theme, setTheme] = useState<ThemeName>("dark");
  const [lang, setLang] = useState("python");
  const [code, setCode] = useState(HELLO.python);
  const [stdin, setStdin] = useState("World");
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const sync = () => setTheme(currentTheme());
    sync();
    window.addEventListener("lc-theme", sync);
    return () => window.removeEventListener("lc-theme", sync);
  }, []);

  useEffect(() => {
    const l = safeGet("lc-play-lang");
    if (l) setLang(l);
    setStdin(safeGet("lc-play-stdin") ?? "World");
  }, []);
  useEffect(() => { setCode(safeGet(`lc-play-code:${lang}`) ?? HELLO[lang] ?? ""); setResult(null); }, [lang]);

  const run = useCallback(async () => {
    if (busy) return;
    setBusy(true); setError(""); setResult(null);
    try {
      setResult(await api<RunResult>("/api/playground/run", { method: "POST", body: JSON.stringify({ language: lang, code, stdin }) }, 120000));
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }, [busy, lang, code, stdin]);

  const runRef = useRef(run);
  runRef.current = run;
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === "Enter" || e.key === "'")) { e.preventDefault(); runRef.current(); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  const languages = meta?.languages ?? [
    { key: "python", label: "Python", editorMode: "python" }, { key: "java", label: "Java", editorMode: "java" },
    { key: "javascript", label: "JavaScript", editorMode: "javascript" }, { key: "cpp", label: "C++", editorMode: "cpp" },
  ];
  const ok = result?.status === "OK";

  return (
    <>
      <h2 style={{ marginBottom: 4 }}>Playground</h2>
      <p className="mute" style={{ marginTop: 0 }}>Run any program with your own input. Nothing here is judged or saved on the server.</p>
      <div className="bar" style={{ marginBottom: 8 }}>
        <select value={lang} aria-label="Language" onChange={(e) => { setLang(e.target.value); safeSet("lc-play-lang", e.target.value); }}>
          {languages.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
        </select>
        <button onClick={() => { safeSet(`lc-play-code:${lang}`, HELLO[lang] ?? ""); setCode(HELLO[lang] ?? ""); }}>Reset</button>
        <span className="grow" />
        <button className="primary" disabled={busy} onClick={run} title="Ctrl/⌘ + Enter">{busy ? "Running…" : "▶ Run"}</button>
      </div>
      <div className="pane" style={{ height: "46vh", minHeight: 260 }}>
        <Editor height="100%" theme={monacoTheme(ed.editorTheme, theme)}
          language={languages.find((l) => l.key === lang)?.editorMode ?? "plaintext"} value={code}
          onChange={(v) => { setCode(v ?? ""); safeSet(`lc-play-code:${lang}`, v ?? ""); }}
          options={{ minimap: { enabled: ed.minimap }, fontSize: ed.fontSize, tabSize: ed.tabSize, insertSpaces: true,
            wordWrap: ed.wordWrap ? "on" : "off", lineNumbers: ed.lineNumbers ? "on" : "off", automaticLayout: true, scrollBeyondLastLine: false }} />
      </div>
      <div className="play-io">
        <div>
          <div className="iolabel">Input (stdin)</div>
          <textarea className="consoletext" spellCheck={false} value={stdin} aria-label="Standard input"
            onChange={(e) => { setStdin(e.target.value); safeSet("lc-play-stdin", e.target.value); }} />
        </div>
        <div>
          <div className="iolabel">Output</div>
          <div className="pane console" style={{ minHeight: 120, padding: 10 }}>
            {busy && <span className="mute">Running…</span>}
            {error && !busy && <div className="banner err" style={{ margin: 0 }}>{error}</div>}
            {result && !busy && (
              <>
                <b className={ok ? "ACCEPTED" : "WRONG_ANSWER"}>{STATUS_TEXT[result.status] ?? result.status}</b>
                <span className="mute">
                  {result.timeMs != null ? ` · ${result.timeMs} ms` : ""}{result.memoryKb != null ? ` · ${(result.memoryKb / 1024).toFixed(1)} MB` : ""}
                </span>
                {result.compileOutput && <pre className="err">{result.compileOutput}</pre>}
                {result.stdout && <pre>{result.stdout}</pre>}
                {result.stderr && <pre className="err">{result.stderr}</pre>}
                {ok && !result.stdout && !result.stderr && <div className="mute">(no output)</div>}
              </>
            )}
            {!result && !busy && !error && <span className="mute">Press Run (Ctrl/⌘ + Enter) to see the output.</span>}
          </div>
        </div>
      </div>
    </>
  );
}
