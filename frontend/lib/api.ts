import { loading } from "./loading";

/** Same-origin: next.config.mjs rewrites /api/* to the backend, so there is no CORS and no preflight. */
export const API = "";

export type Difficulty = "EASY" | "MEDIUM" | "HARD";
export type Status = "TODO" | "ATTEMPTED" | "SOLVED";
/** Language key as served by GET /api/meta (e.g. "java", "cpp"); the set is owned by the backend. */
export type Lang = string;

export interface ProblemSummary {
  id: number; slug: string; title: string; difficulty: Difficulty;
  tags: string[]; status: Status; bookmarked: boolean;
  /** Percent of all submissions that were accepted; null/absent until someone submits. */
  acceptance?: number | null;
  /** Position in the study path; shown as the problem's number. Falls back to id for older servers. */
  number?: number | null;
}
export interface ProblemDetail extends ProblemSummary {
  description: string; starterCode: Record<string, string>;
  samples: { input: string; expectedOutput: string }[];
}
export interface Page<T> { items: T[]; page: number; size: number; totalElements: number; totalPages: number }
export interface CaseResult {
  index: number; sample: boolean; passed: boolean; verdict: string;
  input: string | null; expected: string | null; actual: string | null; error: string | null; timeMs: number | null;
}
export interface RunResponse {
  verdict: string; passed: number; total: number; runtimeMs: number | null; memoryKb?: number | null;
  message: string | null; cases: CaseResult[]; submissionId: number | null;
}
export interface Submission {
  id: number; language: Lang; verdict: string; passed: number; total: number;
  runtimeMs: number | null; memoryKb?: number | null; createdAt: string; code: string;
}
export interface Bin { from: number; to: number; count: number }
/** How one measurement compares with other accepted submissions in the same language. */
export interface Distribution { value: number; beatsPercent: number | null; userBin: number; bins: Bin[] }
export interface SubmissionStats {
  submissionId: number; language: Lang; sampleSize: number; runtime: Distribution | null; memory: Distribution | null;
}
export interface Progress {
  total: number; solved: number; attempted: number; bookmarked: number;
  byDifficulty: Record<string, { total: number; solved: number }>;
}
export interface MetaOption { key: string; label: string }
export interface LanguageOption { key: string; label: string; editorMode: string }
export interface Meta {
  difficulties: MetaOption[]; statuses: MetaOption[]; languages: LanguageOption[];
  defaultLanguage: string; pageSize: number;
}
export interface Topic { tag: string; total: number; solved: number; byDifficulty: Record<string, number> }
/** "hash-table" -> "Hash Table" */
export const tagLabel = (tag: string): string => tag.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
export interface DayCount { date: string; count: number }
export interface RecentSolve { slug: string; title: string; difficulty: Difficulty; language: string; at: string }
export interface ProfileInfo {
  displayName: string; username: string; headline: string; company: string; location: string;
  school: string; website: string; github: string; linkedin: string; tags: string[];
}
export interface Badge {
  id: string; title: string; description: string; category: string; target: number; progress: number; earned: boolean;
}
export interface Profile {
  progress: Progress; attempting: number; submissionsPastYear: number; activeDays: number;
  maxStreak: number; currentStreak: number; calendar: DayCount[]; recentAccepted: RecentSolve[];
  skills: { tag: string; solved: number }[]; languages: { language: string; solved: number }[];
  badges: Badge[];
}
export interface Study { hints: string[]; approach: string; time: string; space: string }
export interface Plan {
  id: string; title: string; blurb: string; total: number; solved: number; problems: ProblemSummary[];
}
export interface Daily { date: string; problem: ProblemSummary }
export interface ExecutionStatus { enabled: boolean; reachable: boolean; provider: string; message: string }

export class ApiError extends Error {
  constructor(message: string, public status: number, public transient: boolean) { super(message); }
}

export function clientId(): string {
  let id = localStorage.getItem("lc-client-id");
  if (!id) { id = crypto.randomUUID(); localStorage.setItem("lc-client-id", id); }
  return id;
}

/** Every failure becomes an ApiError with a message that can be shown to the user as-is. */
export async function api<T>(path: string, init: RequestInit = {}, timeoutMs = 30000): Promise<T> {
  const tracked = !init.method || init.method === "GET";
  if (tracked) loading.start();
  try { return await request<T>(path, init, timeoutMs); } finally { if (tracked) loading.end(); }
}

async function request<T>(path: string, init: RequestInit, timeoutMs: number): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  let res: Response;
  try {
    res = await fetch(`${API}${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", "X-Client-Id": clientId(), ...(init.headers ?? {}) },
    });
  } catch (e) {
    const aborted = (e as Error).name === "AbortError";
    throw new ApiError(
      aborted
        ? "The server is slow to respond."
        : "Can't reach the server.",
      0, true);
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    let msg = "";
    try { const j = await res.json(); msg = j.detail || j.message || j.title || ""; } catch {}
    const transient = res.status === 502 || res.status === 503 || res.status === 504;
    if (!msg) msg = transient ? "The server is starting up." : `Request failed (HTTP ${res.status}).`;
    throw new ApiError(msg, res.status, transient);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

/** Retries transient failures (cold start) so a sleeping free-tier server recovers without the user doing anything. */
export async function apiWithWake<T>(
  path: string, onWaiting: (attempt: number) => void, tries = 30, delayMs = 6000,
): Promise<T> {
  loading.start(); // stays "loading" across silent retries while a sleeping server wakes up
  try {
    for (let attempt = 1; ; attempt++) {
      try { return await api<T>(path, {}, 20000); }
      catch (e) {
        if (!(e instanceof ApiError) || !e.transient || attempt >= tries) throw e;
        onWaiting(attempt);
        await new Promise((r) => setTimeout(r, delayMs));
      }
    }
  } finally { loading.end(); }
}

/** Every problem, following pagination (the server caps page size at 100). */
export async function fetchAllProblems(): Promise<ProblemSummary[]> {
  const out: ProblemSummary[] = [];
  for (let page = 0; ; page++) {
    const d = await api<Page<ProblemSummary>>(`/api/problems?page=${page}&size=100`, {}, 20000);
    out.push(...d.items);
    if (page + 1 >= d.totalPages) return out;
  }
}

/** The browser's own calendar day as YYYY-MM-DD, so the server picks the daily problem for the user's local date. */
export function localDate(d = new Date()): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** IANA time zone of the browser (e.g. Asia/Kolkata) so the server rolls days over at the user's midnight. */
export function localZone(): string {
  try { return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"; } catch { return "UTC"; }
}
export const profilePath = () => `/api/profile?zone=${encodeURIComponent(localZone())}`;
