"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import { API, apiWithWake, ExecutionStatus, ProblemDetail, ProblemSummary } from "./api";
import { cacheGet, loadAll } from "./local";

// Every problem (text, starter code, samples) ships with the site as frontend/public/problems-snapshot.json, generated from
// the backend seed by scripts/build-snapshot.py. The problem list and every problem page render instantly from it; the
// backend only adds progress and bookmarks, and runs code.

type CatalogRow = Pick<ProblemSummary, "id" | "slug" | "title" | "difficulty" | "tags">;
export type StaticProblem = Pick<ProblemDetail, "description" | "starterCode" | "samples">;
type SnapshotRow = CatalogRow & StaticProblem;

let snapPromise: Promise<SnapshotRow[]> | null = null;
function fetchSnapshot(): Promise<SnapshotRow[]> {
  if (!snapPromise) {
    snapPromise = fetch("/problems-snapshot.json")
      .then((r) => { if (!r.ok) throw new Error(`problem data ${r.status}`); return r.json() as Promise<SnapshotRow[]>; })
      .catch((e) => { snapPromise = null; throw e; });
  }
  return snapPromise;
}

export function fetchCatalog(): Promise<CatalogRow[]> {
  return fetchSnapshot().then((rows) => rows.map(({ id, slug, title, difficulty, tags }) => ({ id, slug, title, difficulty, tags })));
}

export async function fetchStaticProblem(slug: string): Promise<StaticProblem | null> {
  try {
    const row = (await fetchSnapshot()).find((p) => p.slug === slug);
    return row ? { description: row.description, starterCode: row.starterCode, samples: row.samples } : null;
  } catch { return null; }
}

export type ServerState = "checking" | "waking" | "online" | "offline";

/** The catalog merged with the user's progress. `server` says whether the backend (progress, running code) is reachable. */
export function useCatalog() {
  const [base, setBase] = useState<CatalogRow[]>([]);
  const [overlay, setOverlay] = useState<Map<string, ProblemSummary>>(() => new Map());
  const [server, setServer] = useState<ServerState>("checking");
  const [attempt, setAttempt] = useState(0);
  const [loadError, setLoadError] = useState("");

  useEffect(() => { fetchCatalog().then(setBase).catch((e) => setLoadError(String(e.message ?? e))); }, []);

  useEffect(() => {
    const saved = cacheGet<ProblemSummary[]>("all");
    if (saved) setOverlay(new Map(saved.map((p) => [p.slug, p])));
    setServer("checking");
    let alive = true;
    loadAll((items) => { if (alive) setOverlay(new Map(items.map((p) => [p.slug, p]))); }, () => { if (alive) setServer("waking"); })
      .then(() => alive && setServer("online"))
      .catch(() => alive && setServer("offline"));
    return () => { alive = false; };
  }, [attempt]);

  const items: ProblemSummary[] = useMemo(
    () => base.map((b) => {
      const o = overlay.get(b.slug);
      return { ...b, status: o?.status ?? "TODO", bookmarked: o?.bookmarked ?? false, acceptance: o?.acceptance ?? null };
    }),
    [base, overlay],
  );
  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  return { items, ready: base.length > 0, server, retry, loadError };
}

/** Waits (with retries) until the backend answers, so Run/Submit do not fail against a sleeping free-tier server. */
export function ensureAwake(onWaiting: (attempt: number) => void): Promise<ExecutionStatus> {
  return apiWithWake<ExecutionStatus>("/api/execution/status", onWaiting, 14, 6000);
}

/** Fire-and-forget request that starts waking a sleeping server before the user needs it. */
export function pingServer() {
  try {
    const k = "lc-ping";
    const last = Number(sessionStorage.getItem(k) ?? 0);
    if (Date.now() - last < 4 * 60 * 1000) return;
    sessionStorage.setItem(k, String(Date.now()));
  } catch { /* storage blocked: ping anyway */ }
  fetch(`${API}/actuator/health`, { mode: "no-cors", cache: "no-store" }).catch(() => {});
}
