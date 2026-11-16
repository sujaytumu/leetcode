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

export function clientId(): string {
  let id = localStorage.getItem("lc-client-id");
  if (!id) { id = crypto.randomUUID(); localStorage.setItem("lc-client-id", id); }
  return id;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Client-Id": clientId(), ...(init.headers ?? {}) },
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try { const j = await res.json(); msg = j.message || j.error || msg; } catch {}
    throw new Error(msg);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}
