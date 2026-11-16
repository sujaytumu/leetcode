export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export type Difficulty = "EASY" | "MEDIUM" | "HARD";
export type Status = "TODO" | "ATTEMPTED" | "SOLVED";
export type Lang = "java" | "python" | "javascript" | "cpp";

export interface ProblemSummary {
  id: number; slug: string; title: string; difficulty: Difficulty;
  tags: string[]; status: Status; bookmarked: boolean;
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
  verdict: string; passed: number; total: number; runtimeMs: number | null;
  message: string | null; cases: CaseResult[]; submissionId: number | null;
}
export interface Submission {
  id: number; language: Lang; verdict: string; passed: number; total: number;
  runtimeMs: number | null; createdAt: string; code: string;
}
export interface Progress {
  total: number; solved: number; attempted: number; bookmarked: number;
  byDifficulty: Record<string, { total: number; solved: number }>;
}
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
        ? "The server took too long to respond. It may still be waking up (free tier) — try again in a minute."
        : "Can't reach the server. It may be waking up (free tier takes 1–3 min) or you're offline.",
      0, true);
  } finally {
    clearTimeout(timer);
  }
  if (!res.ok) {
    let msg = "";
    try { const j = await res.json(); msg = j.detail || j.message || j.title || ""; } catch {}
    const transient = res.status === 502 || res.status === 503 || res.status === 504;
    if (!msg) msg = transient ? "The server is starting up or busy. Try again shortly." : `Request failed (HTTP ${res.status}).`;
    throw new ApiError(msg, res.status, transient);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

/** Retries transient failures (cold start) so a sleeping free-tier server recovers without the user doing anything. */
export async function apiWithWake<T>(
  path: string, onWaiting: (attempt: number) => void, tries = 12, delayMs = 8000,
): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try { return await api<T>(path, {}, 20000); }
    catch (e) {
      if (!(e instanceof ApiError) || !e.transient || attempt >= tries) throw e;
      onWaiting(attempt);
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}
