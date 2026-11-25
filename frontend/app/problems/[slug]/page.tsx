"use client";
import ThemeToggle from "@/components/ThemeToggle";
import AccountMenu from "@/components/AccountMenu";
import dynamic from "next/dynamic";
import Markdown from "react-markdown";
import { type ComponentType, type PointerEvent as RPointerEvent, use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Answer, api, ApiError, ExecutionStatus, Lang, ProblemDetail, ProblemSummary, RunResponse,
  Study, Submission, tagLabel,
} from "@/lib/api";
import { pushRecent } from "@/lib/recent";
import { loadAll, swr } from "@/lib/local";
import { useMeta } from "@/lib/meta";
import { useBackClose } from "@/lib/useBackClose";
import { useCloudSync } from "@/lib/cloud";
import { useMock } from "@/lib/mock";
import VoteButtons from "@/components/VoteButtons";
import ProblemDescription from "@/components/ProblemDescription";
import { formatInputParts, formatOutput } from "@/lib/example";
import { monacoTheme, registerThemes, useEditorSettings } from "@/lib/editorSettings";
import Skeleton from "@/components/Skeleton";
import Logo from "@/components/Logo";
import SubmissionStatsPanel, { fmtMem } from "@/components/SubmissionStatsPanel";
import { usePageTitle } from "@/lib/usePageTitle";
import { fmtSecs, recordTime, type TimeRecord } from "@/lib/times";
import CaseEditor from "@/components/CaseEditor";
import { composeProgram, extractUser, type Parts, shiftErrorLines, splitTemplate } from "@/lib/harness";
import { currentTheme, type ThemeName } from "@/components/ThemeToggle";
import { rememberProblem } from "@/components/ContinueCard";
import { lineDiff } from "@/lib/lineDiff";

import type { EditorProps } from "@monaco-editor/react";

// Loaded on demand: they are only needed once their tab or modal opens, which keeps the first paint fast.
const Solutions = dynamic(() => import("@/components/Solutions"), { ssr: false });
const Discuss = dynamic(() => import("@/components/Discuss"), { ssr: false });
const CodeDiff = dynamic(() => import("@/components/CodeDiff"), { ssr: false });
const SimilarProblems = dynamic(() => import("@/components/SimilarProblems"), { ssr: false });
const EditorSettingsModal = dynamic(() => import("@/components/EditorSettingsModal"), { ssr: false });
const Confetti = dynamic(() => import("@/components/Confetti"), { ssr: false });
const AddToList = dynamic(() => import("@/components/AddToList"), { ssr: false });
const ProblemListDrawer = dynamic(() => import("@/components/ProblemListDrawer"), { ssr: false });
const NoteBox = dynamic(() => import("@/components/NoteBox"), { ssr: false });
const FreeSpace = dynamic(() => import("@/components/FreeSpace"), { ssr: false });
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
  const router = useRouter();
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
  const [tab, setTab] = useState<"desc" | "editorial" | "solutions" | "discuss" | "history" | "notes">("desc");
  // Deep link from the problem list: /problems/two-sum?tab=solutions
  useEffect(() => {
    try {
      const t = new URLSearchParams(window.location.search).get("tab");
      if (t === "solutions" || t === "editorial" || t === "discuss") setTab(t);
      else if (t === "submissions" || t === "history") { setTab("history"); setTimeout(() => loadHistoryRef.current?.(), 0); }
    } catch { /* no URL access: stay on Description */ }
  }, [slug]);
  const loadHistoryRef = useRef<(() => unknown) | null>(null);
  const [consoleTab, setConsoleTab] = useState<"case" | "result">("case");
  const [customInput, setCustomInput] = useState("");
  const [notes, setNotes] = useState("");
  const [ed, setEd, resetEd] = useEditorSettings();
  const fontSize = ed.fontSize;
  const [showSettings, setShowSettings] = useState(false);
  const [history, setHistory] = useState<Submission[]>([]);
  const [openSub, setOpenSub] = useState<Submission | null>(null);
  const [codeExpanded, setCodeExpanded] = useState(false);
  const [diffWith, setDiffWith] = useState<number | "">("");
  const [exec, setExec] = useState<ExecutionStatus | null>(null);
  const [all, setAll] = useState<ProblemSummary[]>([]);
  const { locked } = useMock();
  const [hintsShown, setHintsShown] = useState(0);
  const [showApproach, setShowApproach] = useState(false);
  const [timer, setTimer] = useState({ on: false, secs: 0 });
  const timerRef = useRef(timer); timerRef.current = timer;
  const [solveTime, setSolveTime] = useState<{ rec: TimeRecord; improved: boolean; secs: number } | null>(null);
  const [theme, setTheme] = useState<ThemeName>("dark");
  const [leftPct, setLeftPct] = useState(42);
  const [editorPct, setEditorPct] = useState(60);
  const [drag, setDrag] = useState<"" | "v" | "h">("");
  const [study, setStudy] = useState<Study | null>(null);
  const [focus, setFocus] = useState(false);
  const [copied, setCopied] = useState(false);
  const [topicsOpen, setTopicsOpen] = useState(false);
  const [companiesNote, setCompaniesNote] = useState(false);
  const [burst, setBurst] = useState(0);
  const [streak, setStreak] = useState<number | null>(null);
  useEffect(() => { api<{ currentStreak: number }>("/api/profile").then((p) => setStreak(p.currentStreak ?? 0)).catch(() => {}); }, []);
  const [commentCount, setCommentCount] = useState<number | null>(null);
  const [linkCopied, setLinkCopied] = useState(false);
  const [cursor, setCursor] = useState({ ln: 1, col: 1 });
  const [showKeys, setShowKeys] = useState(false);
  const [showList, setShowList] = useState(false);
  const [answer, setAnswer] = useState<AnswerState>({ status: "idle" });
  const [answerLang, setAnswerLang] = useState("");
  const [runParts, setRunParts] = useState<Parts | null>(null);
  // Phones show one pane at a time (Problem / Code / Result); laptops ignore this and show everything.
  const [pane, setPane] = useState<"problem" | "code" | "result">("problem");
  useBackClose(pane !== "problem", () => setPane("problem")); // phone Back goes Result/Code -> Problem before leaving the page
  const [savedCases, setSavedCases] = useState<string[]>([]);
  const [undoReset, setUndoReset] = useState<string | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);
  const codeRef = useRef(code); codeRef.current = code;
  const pendingRef = useRef<{ lang: string; code: string } | null>(null);
  const slugRef = useRef(slug);
  slugRef.current = slug;
  const workspaceRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLElement>(null);

  // The editor shows only the user's part; the judge gets the full program (hidden shell + user code).
  const parts = useMemo(
    () => (problem && lang ? splitTemplate(problem.starterCode[lang] ?? "", lang, { slug: problem.slug, java: problem.starterCode.java }) : null), [problem, lang]);
  const draftKey = (l: Lang) => `lc-draft2:${slug}:${l}`;
  // Notes and code drafts are mirrored to the server so they follow the device sync code.
  const langRef = useRef(lang); langRef.current = lang;
  const cloud = useCloudSync(slug, {
    onNotes: setNotes,
    onDraft: (l, c) => { if (l === langRef.current) setCode(c); },
  });
  const loadHistory = useCallback(
    () => api<Submission[]>(`/api/problems/${slug}/submissions`).then(setHistory).catch(() => {}), [slug]);
  useEffect(() => { loadHistoryRef.current = loadHistory; }, [loadHistory]);
  // A sleeping free-tier server fails this check for a while; retry quietly before telling the user execution is down.
  const checkExec = useCallback(function check(tries = 0): Promise<void> {
    return api<ExecutionStatus>("/api/execution/status", {}, 20000).then(setExec)
      .catch((e: ApiError) => {
        if (typeof tries === "number" && tries < 12) { setTimeout(() => { void check(tries + 1); }, 5000); return; }
        setExec({ enabled: true, reachable: false, provider: "unknown", message: e.message });
      });
  }, []);

  const loadProblem = useCallback(() => {
    setLoadError("");
    swr<ProblemDetail>(`/api/problems/${slug}`, (p) => setProblem(p), () => {})
      .catch((e) => setLoadError(e.message));
  }, [slug]);

  useEffect(() => {
    if (problem) pushRecent({ slug: problem.slug, title: problem.title, number: problem.number, difficulty: problem.difficulty });
  }, [problem?.slug]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { loadProblem(); loadHistory(); checkExec(); }, [loadProblem, loadHistory, checkExec]);
  useEffect(() => {
    if (!meta || lang) return;
    // C++ is the main language: ?lang= from a link wins, then your last choice, then C++, then the server default.
    const ok = (k: string | null) => !!k && meta.languages.some((x) => x.key === k);
    const asked = new URLSearchParams(window.location.search).get("lang");
    const saved = localStorage.getItem("lc-lang");
    const pick = ok(asked) ? asked! : ok(saved) ? saved! : ok("cpp") ? "cpp" : meta.defaultLanguage;
    if (ok(asked)) localStorage.setItem("lc-lang", pick);
    setLang(pick);
  }, [meta, lang]);
  useEffect(() => {
    let live = true;
    setStudy(null);
    api<Study | undefined>(`/api/problems/${slug}/study`)
      .then((s) => { if (live) setStudy(s ?? null); })
      .catch(() => { if (live) setStudy(null); });
    return () => { live = false; };
  }, [slug]);
  useEffect(() => { if (problem && problem.slug === slug) rememberProblem(slug, problem.title); }, [problem, slug]);
  const [showDiff, setShowDiff] = useState(false);
  usePageTitle(problem ? `${problem.number ?? problem.id}. ${problem.title}` : "Problem");
  const hasProblem = problem !== null;
  useEffect(() => { if (hasProblem) loadAll((items) => setAll(items), () => {}).catch(() => {}); }, [hasProblem]);
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("lc-layout-v2") ?? "null") as { leftPct?: number; editorPct?: number } | null;
      if (saved?.leftPct) setLeftPct(clamp(saved.leftPct, 22, 70));
      if (saved?.editorPct) setEditorPct(clamp(saved.editorPct, 20, 80));
    } catch { /* ignore corrupt layout */ }
  }, []);
  useEffect(() => {
    try { localStorage.setItem("lc-layout-v2", JSON.stringify({ leftPct, editorPct })); } catch { /* storage blocked */ }
  }, [leftPct, editorPct]);
  useEffect(() => {
    const sync = () => setTheme(currentTheme());
    sync();
    window.addEventListener("lc-theme", sync);
    return () => window.removeEventListener("lc-theme", sync);
  }, []);
  useEffect(() => { setNotes(localStorage.getItem(`lc-notes:${slug}`) ?? ""); }, [slug]);
  useEffect(() => {
    try {
      const v = JSON.parse(localStorage.getItem(`lc-cases:${slug}`) ?? "[]");
      setSavedCases(Array.isArray(v) ? v.filter((x): x is string => typeof x === "string").slice(0, 20) : []);
    } catch { setSavedCases([]); }
    setUndoReset(null);
  }, [slug]);
  useEffect(() => { setAnswer({ status: "idle" }); setAnswerLang(""); }, [slug]);
  useEffect(() => { if (locked(slug) && (tab === "editorial" || tab === "solutions")) setTab("desc"); }, [locked, slug, tab]);
  useEffect(() => { setHintsShown(0); setShowApproach(false); setTimer({ on: false, secs: 0 }); setPane("problem"); }, [slug]);
  // Start the console on the first sample whenever a different problem is opened.
  useEffect(() => {
    if (problem) { setCustomInput(problem.samples[0]?.input ?? ""); setResult(null); setSolveTime(null); setConsoleTab("case"); }
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

  const onChange = (v?: string) => { setCode(v ?? ""); localStorage.setItem(draftKey(lang), v ?? ""); cloud.saveDraft(lang, v ?? ""); };

  const run = useCallback(async (kind: "run" | "submit") => {
    if (busy) return;
    const custom = kind === "run" && isCustomInput(problem, customInput);
    setBusy(kind); setError(""); setMode(kind); setCustomRun(custom); setResult(null); setCaseTab(0);
    setConsoleTab("result");
    setPane("result");
    setRunParts(parts);
    try {
      const source = parts ? composeProgram(parts, code) : code;
      const r = await api<RunResponse>(`/api/problems/${slug}/${kind}`,
        { method: "POST", body: JSON.stringify({ language: lang, code: source, ...(custom ? { customInput } : {}) }) }, 120000);
      setResult(r);
      if (kind === "submit" && r.verdict === "ACCEPTED") setBurst((b) => b + 1);
      const firstFail = r.cases.findIndex((c) => !c.passed);
      setCaseTab(firstFail >= 0 ? firstFail : 0);
      if (kind === "submit") {
        // Like LeetCode: jump to the Submissions tab and open the submission that was just judged.
        api<Submission[]>(`/api/problems/${slug}/submissions`).then((h) => {
          setHistory(h);
          const mine = (r.submissionId != null ? h.find((x) => x.id === r.submissionId) : undefined) ?? h[0];
          if (mine && slugRef.current === slug) { setDiffWith(""); setOpenSub(mine); setTab("history"); }
        }).catch(() => {});
        // Only a running or paused timer with time on it counts as a timed solve.
        const secs = timerRef.current.secs;
        if (r.verdict === "ACCEPTED" && !custom && secs > 0) setSolveTime({ ...recordTime(slug, secs), secs });
        else setSolveTime(null);
      }
      checkExec();
    } catch (e) {
      setError((e as Error).message);
      checkExec();
    } finally { setBusy(""); }
  }, [busy, slug, lang, code, parts, problem, customInput, loadHistory, checkExec]);

  const allRef = useRef(all); allRef.current = all;
  const runRef = useRef(run);
  runRef.current = run;
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "'") { e.preventDefault(); runRef.current("run"); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runRef.current("submit"); }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault(); // drafts autosave on every keystroke; this just confirms it and stops the browser's save dialog
        setSavedFlash(true); setTimeout(() => setSavedFlash(false), 1400);
      }
      if (e.key === "Escape") { setShowKeys(false); setShowSettings(false); setFocus(false); }
      // Alt+Shift+N / P: next / previous problem in the list order (e.code, because Alt changes e.key on macOS).
      if (e.altKey && e.shiftKey && (e.code === "KeyN" || e.code === "KeyP")) {
        const list = allRef.current, i = list.findIndex((p) => p.slug === slugRef.current);
        const to = i >= 0 ? list[i + (e.code === "KeyN" ? 1 : -1)] : undefined;
        if (to) { e.preventDefault(); router.push(`/problems/${to.slug}`); }
      }
      const el = e.target as HTMLElement | null;
      const typing = !!el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT" || el.isContentEditable);
      if (e.key === "?" && !typing && !e.ctrlKey && !e.metaKey) setShowKeys((v) => !v);
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  useEffect(() => {
    let live = true;
    setCommentCount(null); setTopicsOpen(false);
    api<unknown[]>(`/api/problems/${slug}/comments`).then((c) => { if (live && Array.isArray(c)) setCommentCount(c.length); }).catch(() => {});
    return () => { live = false; };
  }, [slug]);

  async function toggleBookmark() {
    if (!problem) return;
    try {
      await api(`/api/problems/${slug}/bookmark`, { method: problem.bookmarked ? "DELETE" : "PUT" });
      setProblem({ ...problem, bookmarked: !problem.bookmarked });
    } catch (e) { setError((e as Error).message); }
  }

  /** Jump to a random other problem, like LeetCode's shuffle button. */
  function shuffle() {
    const others = all.filter((p) => p.slug !== slug);
    if (others.length) router.push(`/problems/${others[Math.floor(Math.random() * others.length)].slug}`);
  }

  async function shareLink() {
    try { await navigator.clipboard.writeText(window.location.href); setLinkCopied(true); setTimeout(() => setLinkCopied(false), 1500); }
    catch { /* clipboard blocked: nothing useful to do */ }
  }

  async function copyCode() {
    try { await navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 1500); }
    catch { setError("Could not copy: clipboard access was blocked by the browser."); }
  }

  function reset() {
    if (!problem) return;
    const initial = parts ? parts.stub : problem.starterCode[lang] ?? "";
    if (norm(codeRef.current) === norm(initial)) return;
    setUndoReset(codeRef.current);
    localStorage.removeItem(draftKey(lang)); cloud.clearDraft(lang); setCode(initial);
  }

  function undoResetCode() {
    if (undoReset === null) return;
    setCode(undoReset); localStorage.setItem(draftKey(lang), undoReset); cloud.saveDraft(lang, undoReset);
    setUndoReset(null);
  }

  function persistCases(next: string[]) {
    setSavedCases(next);
    try { localStorage.setItem(`lc-cases:${slug}`, JSON.stringify(next)); } catch { /* storage blocked */ }
  }

  function loadSubmission(s: Submission) {
    const user = extractUser(s.code, s.language) ?? splitTemplate(s.code, s.language)?.stub ?? null;
    if (user === null) {
      setError("This older submission was saved as a full program and can't be opened in the simplified editor.");
      setConsoleTab("result");
      return;
    }
    if (s.language === lang) { setCode(user); localStorage.setItem(draftKey(lang), user); cloud.saveDraft(lang, user); }
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
          // The editor's share of the right column; the pointer sits on the divider, so subtract half its height.
          setEditorPct(clamp(((ev.clientY - r.top - 4) / r.height) * 100, 20, 80));
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
          <button onClick={() => { void checkExec(); }}>Re-check</button>
        </div>
      )}
      <div className="lctop">
        <div className="lctop-l">
          <Confetti burst={burst} />
          <Link href="/" className="lclogo" title="LeetCode Practice home" aria-label="Home"><Logo size={28} /></Link>
          <button className="lclist" onClick={() => setShowList(true)} title="Problem list">☰ <span className="hide-sm">Problem List</span></button>
          {prev ? <Link className="navbtn" href={`/problems/${prev.slug}`} title={prev.title} aria-label="Previous problem">‹</Link> : <span className="navbtn off" aria-hidden="true">‹</span>}
          {next ? <Link className="navbtn" href={`/problems/${next.slug}`} title={next.title} aria-label="Next problem">›</Link> : <span className="navbtn off" aria-hidden="true">›</span>}
          <button onClick={shuffle} title="Pick a random problem" aria-label="Random problem">⤮</button>
        </div>
        <div className="lctop-c runbar">
            <button disabled={!!busy} onClick={() => run("run")} title="Ctrl/⌘ + '">
              {busy === "run" ? `Running… ${elapsed}s` : custom ? "▶ Run custom" : "▶ Run"}
            </button>
            <button className="primary" disabled={!!busy} onClick={() => run("submit")} title="Ctrl/⌘ + Enter">
              {busy === "submit" ? `Judging… ${elapsed}s` : "Submit"}
            </button>
        </div>
        <div className="lctop-r">
          <button className="topicon" onClick={() => setTab(tab === "notes" ? "desc" : "notes")} title="Notes" aria-label="Notes">📝</button>
          <Link className="topicon streak" href="/daily" title="Daily challenge streak" aria-label="Daily challenge streak">🔥<span>{streak ?? 0}</span></Link>
          <button onClick={() => setTimer((x) => ({ ...x, on: !x.on }))} title="Stopwatch for this attempt">
            ⏱ {clock}{timer.on ? " ⏸" : timer.secs ? " ▶" : ""}
          </button>
          <div className="nav-end"><ThemeToggle /><AccountMenu /></div>
        </div>
      </div>
      <div ref={workspaceRef} data-pane={pane} className={`workspace${drag ? " dragging" : ""}${focus ? " focus" : ""}`}
        style={{ gridTemplateColumns: focus ? "minmax(0, 1fr)" : `${leftPct}% 8px minmax(0, 1fr)` }}>
        <section className="pane left" hidden={focus}>
          <div className="lctabs lcmaintabs">
            <button className={tab === "desc" ? "on" : ""} onClick={() => setTab("desc")}><span className="tabicon ti-desc" aria-hidden="true">▤</span>Description</button>
            <button className={tab === "editorial" ? "on" : ""} disabled={locked(slug)} title={locked(slug) ? "Hidden during a mock interview" : undefined} onClick={() => setTab("editorial")}><span className="tabicon ti-edit" aria-hidden="true">▥</span>Editorial</button>
            <button className={tab === "solutions" ? "on" : ""} disabled={locked(slug)} title={locked(slug) ? "Hidden during a mock interview" : undefined} onClick={() => setTab("solutions")}><span className="tabicon ti-sol" aria-hidden="true">⚗</span>Solutions</button>
            <button className={tab === "history" ? "on" : ""} onClick={() => { setTab("history"); loadHistory(); }}><span className="tabicon ti-sub" aria-hidden="true">◷</span>Submissions</button>
          </div>
          <div className="left-body">
            {tab === "desc" ? (
              <>
                <div className="titlerow">
                  <h2 className="ptitle">{problem.number ?? problem.id}. {problem.title}</h2>
                  {problem.status === "SOLVED" && <span className="solved">Solved<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M8 12.5l3 3 5-6" /></svg></span>}
                </div>
                <div className="pmeta">
                  <span className={`pill chipdiff ${problem.difficulty}`}>{title(problem.difficulty)}</span>
                  {problem.tags.length > 0 && (
                    <button className={`chip${topicsOpen ? " open" : ""}`} onClick={() => setTopicsOpen((o) => !o)} aria-expanded={topicsOpen}>
                      <span aria-hidden="true">⌗</span> Topics
                    </button>
                  )}
                  <button className={`chip lockedchip${companiesNote ? " open" : ""}`} onClick={() => setCompaniesNote((v) => !v)} aria-expanded={companiesNote}>
                    <span aria-hidden="true">🔒</span> Companies
                  </button>
                  {study?.hints?.length ? (
                    <button className="chip" onClick={() => {
                      const d = document.querySelector<HTMLDetailsElement>(".deschints details");
                      if (d) { d.open = true; d.scrollIntoView({ behavior: "smooth", block: "center" }); }
                    }}>
                      <span aria-hidden="true">💡</span> Hint
                    </button>
                  ) : null}
                </div>
                {companiesNote && <div className="pmeta mute" style={{ fontSize: 13 }}>Company tags are not available in this practice app.</div>}
                {topicsOpen && <div className="pmeta">{problem.tags.map((t) => <span className="tag" key={t}>{tagLabel(t)}</span>)}</div>}
                <ProblemDescription markdown={problem.description} python={problem.starterCode?.python} />
                {study?.hints?.length ? (
                  <div className="deschints">
                    {(study.hints ?? []).map((h, i) => (
                      <details key={i}><summary>💡 Hint {i + 1}</summary><p>{h}</p></details>
                    ))}
                  </div>
                ) : null}
                {problem.acceptance != null && (
                  <div className="statstrip mute">Acceptance Rate <b>{problem.acceptance.toFixed(1)}%</b></div>
                )}
                <SimilarProblems current={problem} all={all} />
              </>
            ) : tab === "editorial" ? (
              <div className="editorial">
                {study ? (
                  <div className="study">
                    <h3>Hints</h3>
                    {(study.hints ?? []).slice(0, hintsShown).map((h, i) => (
                      <div className="hint" key={i}><b>Hint {i + 1}.</b> {h}</div>
                    ))}
                    {hintsShown < (study.hints ?? []).length ? (
                      <button onClick={() => setHintsShown(hintsShown + 1)}>
                        {hintsShown === 0 ? "Show a hint" : `Show hint ${hintsShown + 1} of ${(study.hints ?? []).length}`}
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
                <h3>Solution</h3>
                <div className="answer">
                {answer.status === "idle" && (
                  <>
                    <p className="mute">Spoiler: try it yourself first. The hints above do not give it away.</p>
                    <button className="primary" onClick={revealAnswer}>Show solution</button>
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
              </div>
            ) : tab === "solutions" ? (
              <Solutions slug={slug} />
            ) : tab === "discuss" ? (
              <>
                <div className="subhead"><button onClick={() => setTab("desc")}>← Description</button><b>Discuss</b></div>
                <Discuss slug={slug} />
              </>
            ) : tab === "notes" ? (
              <>
                <div className="subhead"><button onClick={() => setTab("desc")}>← Description</button><b>Notes</b></div>
                <p className="mute" style={{ marginBottom: 6 }}>Private notes for this problem, saved on this device.</p>
                <textarea className="notes" placeholder="Your approach, mistakes, edge cases to remember…" value={notes}
                  onChange={(e) => { setNotes(e.target.value); localStorage.setItem(`lc-notes:${slug}`, e.target.value); cloud.saveNotes(e.target.value); }} />
              </>
            ) : (
              openSub ? (
                <div className="subdetail">
                  <button className="ghost backlink" onClick={() => { setOpenSub(null); setDiffWith(""); }}>← All Submissions</button>
                  <div className="subtop">
                    <div>
                      <h3 className={`verdict subverdict ${openSub.verdict}`}>{title(openSub.verdict)}</h3>
                      <div className="mute subpassed">{openSub.passed} / {openSub.total} testcases passed</div>
                      <div className="mute subdate">Submitted at {new Date(openSub.createdAt).toLocaleString(undefined, { month: "short", day: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: false })}</div>
                    </div>
                    <span className="subbtns">
                      <button className="anabtn" onClick={() => { setOpenSub(null); setTab("editorial"); }} title="Approach and complexity analysis">✦ Analysis</button>
                      <button className="solbtn" onClick={() => { setOpenSub(null); setTab("solutions"); }}>✎ Solution</button>
                    </span>
                  </div>
                  {openSub.verdict === "ACCEPTED" && <SubmissionStatsPanel id={openSub.id} />}
                  <div className="subcodehead"><b>Code</b><span className="langchip">{languages.find((l) => l.key === openSub.language)?.label ?? LANG_LABEL[openSub.language] ?? openSub.language}</span></div>
                  <div className="bar" style={{ marginBottom: 6 }}>
                    <select aria-label="Compare with another submission" value={diffWith}
                      onChange={(e) => { setDiffWith(e.target.value ? Number(e.target.value) : ""); setShowDiff(false); }}>
                      <option value="">Compare with another submission…</option>
                      {history.filter((h) => h.id !== openSub.id).map((h) => (
                        <option key={h.id} value={h.id}>Diff vs #{h.id} · {title(h.verdict)} · {new Date(h.createdAt).toLocaleString()}</option>
                      ))}
                    </select>
                  </div>
                  {(() => {
                    const other = diffWith === "" ? null : history.find((h) => h.id === diffWith);
                    // Diff reads old -> new, so the older submission is the "before" side.
                    return other ? <CodeDiff before={other.id < openSub.id ? other.code : openSub.code} after={other.id < openSub.id ? openSub.code : other.code} /> : null;
                  })()}
                  {diffWith !== "" ? null : showDiff ? (
                    <>
                      <div className="mute" style={{ fontSize: 12, marginBottom: 4 }}>Submission → your editor ({lang})</div>
                      <pre className="subcode diff">{lineDiff(openSub.code, code).map((r, i) => (
                        <div key={i} className={`dl ${r.kind}`}>{r.kind === "add" ? "+ " : r.kind === "del" ? "- " : "  "}{r.text}</div>
                      ))}</pre>
                    </>
                  ) : (
                    <div className={`subcodewrap${codeExpanded ? " open" : ""}`}>
                      <pre className="subcode lnum">{openSub.code.replace(/\n+$/, "").split("\n").map((ln, i) => (
                        <div key={i} className="ln"><span className="lno">{i + 1}</span><span>{ln || " "}</span></div>
                      ))}</pre>
                      {openSub.code.split("\n").length > 9 && (
                        <button className="viewmore" onClick={() => setCodeExpanded((v) => !v)}>{codeExpanded ? "︿ View less" : "﹀ View more"}</button>
                      )}
                    </div>
                  )}
                  <button onClick={() => { setLang(openSub.language); setCode(openSub.code); setTab("desc"); setOpenSub(null); }}>Load into editor</button>{" "}
                  <button className="ghost" disabled={openSub.language !== lang} title={openSub.language !== lang ? "Switch the editor to this submission's language to compare" : "Compare with the code in your editor"}
                    onClick={() => setShowDiff((v) => !v)}>{showDiff ? "Hide diff" : "Diff vs editor"}</button>
                  <NoteBox slug={slug} value={notes} tags={problem.tags}
                    onChange={(v) => { setNotes(v); localStorage.setItem(`lc-notes:${slug}`, v); cloud.saveNotes(v); }} />
                </div>
              ) : (
              <table className="subtable">
                <thead><tr><th>Status</th><th>Language</th><th>Runtime</th><th>Memory</th></tr></thead>
                <tbody>
                  {history.map((s) => (
                    <tr key={s.id} className="subrow" onClick={() => setOpenSub(s)} title="Open details">
                      <td className={s.verdict}>
                        <b>{title(s.verdict)}</b>
                        <div className="mute subdate" title={new Date(s.createdAt).toLocaleString()}>
                          {new Date(s.createdAt).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                        </div>
                      </td>
                      <td><span className="langchip">{languages.find((l) => l.key === s.language)?.label ?? LANG_LABEL[s.language] ?? s.language}</span></td>
                      <td><span className="mute" aria-hidden="true">⏱ </span>{s.runtimeMs != null ? `${s.runtimeMs} ms` : "N/A"}</td>
                      <td><span className="mute" aria-hidden="true">▦ </span>{s.memoryKb != null ? fmtMem(s.memoryKb) : "N/A"}</td>
                    </tr>
                  ))}
                  {history.length === 0 && <tr><td colSpan={4} className="mute">No submissions yet. Submit your code to see how it compares.</td></tr>}
                </tbody>
              </table>
              )
            )}
          </div>
          <div className="lcfoot">
            <VoteButtons slug={slug} />
            <button className={tab === "discuss" ? "on" : ""} onClick={() => setTab(tab === "discuss" ? "desc" : "discuss")} title="Discuss">
              💬{commentCount != null ? ` ${commentCount}` : ""}
            </button>
            <button onClick={toggleBookmark} title={problem.bookmarked ? "Remove bookmark" : "Bookmark"} aria-pressed={problem.bookmarked}>{problem.bookmarked ? "★" : "☆"}</button>
            <button onClick={shareLink} title="Copy link to this problem">{linkCopied ? "✔" : "🔗"}</button>
            <button className={tab === "notes" ? "on" : ""} onClick={() => setTab(tab === "notes" ? "desc" : "notes")} title="Notes">📝{notes ? " •" : ""}</button>
            <AddToList slug={slug} />
          </div>
        </section>

        <div hidden={focus} className={`vdivider${drag === "v" ? " drag" : ""}`} role="separator" aria-orientation="vertical"
          title="Drag to resize" onPointerDown={startDrag("v")} />

        <section className="right" ref={rightRef}>
          <div className="pane editor-wrap" style={{ flex: `0 0 ${editorPct}%` }}>
            <div className="codehead"><span className="codeicon" aria-hidden="true">&lt;/&gt;</span><b>Code</b></div>
            <div className="codebar">
              <select className="langpick" aria-label="Language" value={lang} onChange={(e) => { setLang(e.target.value); setUndoReset(null); localStorage.setItem("lc-lang", e.target.value); }}>
                {languages.map((l) => <option key={l.key} value={l.key}>{l.label}</option>)}
              </select>
              <select className="sizepick" value={fontSize} title="Editor font size" aria-label="Editor font size" onChange={(e) => setEd({ fontSize: Number(e.target.value) })}>
                {[12, 14, 16, 18, 20].map((n) => <option key={n} value={n}>{n}px</option>)}
              </select>
              <span className="autotag mute" title="Auto-closing brackets and quotes">🔒 Auto</span>
              {savedFlash && <span className="mute savedtag" role="status">✔ Saved</span>}
              <span className="grow" />
              {undoReset !== null && <button className="iconbtn" onClick={undoResetCode} title="Bring back the code you had before Reset">↶ Undo reset</button>}
              <button className="iconbtn" onClick={reset} title="Reset to starter code" aria-label="Reset to starter code">↺</button>
              <button className="iconbtn" onClick={copyCode} title="Copy your code" aria-label="Copy your code">{copied ? "✔" : "⧉"}</button>
              <button className="iconbtn" onClick={() => setShowSettings(true)} title="Editor settings" aria-label="Editor settings">⚙</button>
              <button className="iconbtn" onClick={() => setShowKeys(true)} title="Keyboard shortcuts (?)" aria-label="Keyboard shortcuts">⌨</button>
              <button className="iconbtn" onClick={() => setFocus((f) => !f)} title="Hide the description and focus on the editor (Esc to exit)" aria-label={focus ? "Exit focus" : "Focus"}>
                {focus ? "⤡" : "⤢"}
              </button>
            </div>
            <div className="codebody">
              <Editor height="100%" beforeMount={registerThemes} onMount={(ed) => { ed.onDidChangeCursorPosition((e) => setCursor({ ln: e.position.lineNumber, col: e.position.column })); }} theme={monacoTheme(ed.editorTheme, theme)}
              language={languages.find((l) => l.key === lang)?.editorMode ?? "plaintext"}
              value={code} onChange={onChange}
              options={{
                minimap: { enabled: ed.minimap }, fontSize, tabSize: ed.tabSize, insertSpaces: true,
                wordWrap: ed.wordWrap ? "on" : "off", lineNumbers: ed.lineNumbers ? "on" : "off",
                automaticLayout: true, scrollBeyondLastLine: false,
              }} />
            </div>
            <div className="codestatus mute"><span>Saved</span><span>Ln {cursor.ln}, Col {cursor.col}</span></div>
          </div>
          <div className={`hdivider${drag === "h" ? " drag" : ""}`} role="separator" aria-orientation="horizontal"
            title="Drag to resize" onPointerDown={startDrag("h")} />
          <div className="pane console result-pane">
            <div className="lctabs">
              <button className={consoleTab === "case" ? "on" : ""} onClick={() => setConsoleTab("case")}><span className="tabicon tc-ok" aria-hidden="true">☑</span>Testcase</button>
              <button className={consoleTab === "result" ? "on" : ""} onClick={() => setConsoleTab("result")}>
                <span className="tabicon tc-term" aria-hidden="true">&gt;_</span>Test Result{result && !busy ? <span className={result.verdict === "ACCEPTED" ? "ACCEPTED" : "WRONG_ANSWER"}> ●</span> : null}
              </button>
            </div>
            <div className="body">
              {consoleTab === "case" ? (
                <>
                  <div className="casechips">
                    {problem.samples.map((s, i) => (
                      <button key={i} className={sampleIdx === i ? "on" : ""} onClick={() => setCustomInput(s.input)}>Case {i + 1}</button>
                    ))}
                    {savedCases.map((c, i) => (
                      <span key={i} className="savedcase">
                        <button className={norm(c) === norm(customInput) ? "on" : ""} onClick={() => setCustomInput(c)} title={c}>My case {i + 1}</button>
                        <button className="linklike" aria-label={`Delete my case ${i + 1}`} title="Delete this saved case"
                          onClick={() => persistCases(savedCases.filter((_, j) => j !== i))}>×</button>
                      </span>
                    ))}
                    {savedCases.length < 20 && (
                      <button className="addcase" aria-label="Add a test case" title="Add a case (starts from the current input)"
                        onClick={() => { const base = customInput || problem.samples[0]?.input || ""; persistCases([...savedCases, base]); setCustomInput(base); }}>+</button>
                    )}
                    {custom && <span className="pill MEDIUM">Custom input</span>}
                    {custom && !savedCases.some((c) => norm(c) === norm(customInput)) && savedCases.length < 20 && (
                      <button onClick={() => persistCases([...savedCases, customInput])} title="Keep this input for next time">＋ Save case</button>
                    )}
                  </div>
                  <CaseEditor python={problem.starterCode.python ?? ""} value={customInput} onChange={setCustomInput} />
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
                      <div className="resulthead">
                        <h3 className={`verdict ${result.verdict}`}>{verdictText}</h3>
                        {result.runtimeMs != null && !customRun && <span className="resultrt">Runtime: {result.runtimeMs} ms</span>}
                      </div>
                      <div className="vstats">
                        {customRun
                          ? "Custom input"
                          : `${result.passed} / ${result.total} testcases passed${mode === "run" ? " · sample cases only" : ""}`}
                        {result.runtimeMs != null && customRun ? ` · Runtime: ${result.runtimeMs} ms` : ""}{result.memoryKb != null ? ` · Memory: ${fmtMem(result.memoryKb)}` : ""}
                      </div>
                      {mode === "submit" && result.verdict === "ACCEPTED" && result.submissionId != null && <div className="consolestats"><SubmissionStatsPanel id={result.submissionId} /></div>}
                      {mode === "submit" && result.verdict === "ACCEPTED" && solveTime && (
                        <div className="vstats" style={{ marginTop: 6 }}>⏱ Solved in <b style={{ display: "inline", fontSize: 14 }}>{fmtSecs(solveTime.secs)}</b>
                          {solveTime.improved ? " · new personal best" : ` · best ${fmtSecs(solveTime.rec.best)}`} ({solveTime.rec.runs} timed solve{solveTime.rec.runs === 1 ? "" : "s"})</div>
                      )}
                      {result.message && <div className={result.verdict === "ACCEPTED" ? "" : "err"}>{fix(result.message)}</div>}
                      {result.cases.length > 1 && (
                        <div className="casechips" style={{ marginTop: 8 }}>
                          {result.cases.map((c, i) => (
                            <button key={i} className={caseTab === i ? "on" : ""} onClick={() => setCaseTab(i)}>
                              <span className={`caseicon ${c.passed ? "ok" : "bad"}`} aria-label={c.passed ? "passed" : "failed"}>{c.passed ? "✓" : "✕"}</span> {c.sample ? `Case ${c.index}` : `Hidden ${c.index}`}
                            </button>
                          ))}
                        </div>
                      )}
                      {cur && (cur.input != null ? (
                        <>
                          {(() => {
                            // LeetCode shows each argument by name; fall back to the raw stdin text if the layout is unknown.
                            const py = problem.starterCode?.python;
                            const args = py ? formatInputParts(py, cur.input) : null;
                            const show = (raw: string) => (py && raw.trim() ? formatOutput(py, raw) : null) ?? raw;
                            return (
                              <>
                                {args
                                  ? <><div className="iosec">Input</div>{args.map((a) => <div key={a.name} className="iobox"><div className="iolabel">{a.name} =</div><pre>{a.value}</pre></div>)}</>
                                  : <><div className="iosec">Input</div><div className="iobox"><pre>{cur.input}</pre></div></>}
                                {cur.stdout ? <><div className="iosec">Stdout</div><div className="iobox"><pre>{cur.stdout}</pre></div></> : null}
                                <div className="iosec">Output</div><div className="iobox"><pre>{cur.actual ? show(cur.actual) : "(empty)"}</pre></div>
                                {cur.expected != null && <><div className="iosec">Expected</div><div className="iobox"><pre>{show(cur.expected)}</pre></div></>}
                              </>
                            );
                          })()}
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
                  {result && !busy && (
                    <a className="contribute" target="_blank" rel="noreferrer"
                      href={`https://github.com/sujaytumu/leetcode/issues/new?title=${encodeURIComponent(`Testcase suggestion: ${problem.title}`)}`}>
                      <span aria-hidden="true">♡</span> Contribute a testcase
                    </a>
                  )}
                  {!result && !busy && !error && <span className="mute">Run or submit to see results. Shortcuts: Ctrl/⌘+' to run, Ctrl/⌘+Enter to submit.</span>}
                </>
              )}
            </div>
          </div>
        </section>
      </div>
      <nav className="mtabs" aria-label="Workspace panes">
        {(["problem", "code", "result"] as const).map((k) => (
          <button key={k} className={pane === k ? "on" : ""} aria-pressed={pane === k} onClick={() => setPane(k)}>
            {k === "problem" ? "📄 Problem" : k === "code" ? "⌨ Code" : <>▶ Result{result && !busy ? <span className={result.verdict === "ACCEPTED" ? "ACCEPTED" : "WRONG_ANSWER"}> ●</span> : null}</>}
          </button>
        ))}
      </nav>
      {showSettings && <EditorSettingsModal settings={ed} onChange={setEd} onReset={resetEd} onClose={() => setShowSettings(false)} />}
      <ProblemListDrawer open={showList} onClose={() => setShowList(false)} problems={all} currentSlug={slug} />
      {showKeys && (
        <div className="modal-back" onClick={() => setShowKeys(false)}>
          <div className="modal" role="dialog" aria-label="Keyboard shortcuts" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Keyboard shortcuts</h3>
            <table>
              <tbody>
                <tr><td><kbd>Ctrl/⌘</kbd> + <kbd>&apos;</kbd></td><td>Run on the console input</td></tr>
                <tr><td><kbd>Ctrl/⌘</kbd> + <kbd>Enter</kbd></td><td>Submit</td></tr>
                <tr><td><kbd>Ctrl/⌘</kbd> + <kbd>S</kbd></td><td>Confirm the draft is saved (it autosaves)</td></tr>
                <tr><td><kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> / <kbd>N</kbd></td><td>Previous / next problem</td></tr>
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
