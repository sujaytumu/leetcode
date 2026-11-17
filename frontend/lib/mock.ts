"use client";
import { useCallback, useEffect, useState } from "react";
import type { ProblemSummary, Status } from "./api";

/** A timed practice session: a few problems, a countdown, and no hints or answers until it ends. */
export interface MockSession {
  id: string; format: string; startedAt: number; durationSec: number; slugs: string[];
  /** Status of each problem when the session started, to tell what was solved during it. */
  baseline: Record<string, Status>; endedAt?: number;
}
export interface MockFormat { key: string; label: string; minutes: number; difficulties: ("EASY" | "MEDIUM" | "HARD")[]; blurb: string }

export const FORMATS: MockFormat[] = [
  { key: "quick", label: "Quick screen", minutes: 30, difficulties: ["EASY", "MEDIUM"], blurb: "One Easy and one Medium in 30 minutes." },
  { key: "standard", label: "Standard interview", minutes: 45, difficulties: ["MEDIUM", "MEDIUM"], blurb: "Two Mediums in 45 minutes." },
  { key: "onsite", label: "Onsite round", minutes: 60, difficulties: ["MEDIUM", "HARD"], blurb: "A Medium and a Hard in 60 minutes." },
];

const KEY = "lc-mock", HISTORY = "lc-mock-history", EVENT = "lc-mock-change";

function read(): MockSession | null {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "null") as MockSession | null; } catch { return null; }
}
function write(s: MockSession | null) {
  try { if (s) localStorage.setItem(KEY, JSON.stringify(s)); else localStorage.removeItem(KEY); } catch { /* storage blocked */ }
  window.dispatchEvent(new Event(EVENT));
}

/** Picks problems for a format: random and unsolved where possible, never the same problem twice. */
export function pickProblems(format: MockFormat, items: ProblemSummary[], rand: () => number = Math.random): ProblemSummary[] {
  const chosen: ProblemSummary[] = [];
  for (const d of format.difficulties) {
    const ofLevel = items.filter((p) => p.difficulty === d && !chosen.some((c) => c.slug === p.slug));
    const fresh = ofLevel.filter((p) => p.status !== "SOLVED");
    const pool = fresh.length ? fresh : ofLevel;
    if (pool.length) chosen.push(pool[Math.floor(rand() * pool.length)]);
  }
  return chosen;
}

export function startSession(format: MockFormat, problems: ProblemSummary[]): MockSession {
  const s: MockSession = {
    id: String(Date.now()), format: format.key, startedAt: Date.now(), durationSec: format.minutes * 60,
    slugs: problems.map((p) => p.slug), baseline: Object.fromEntries(problems.map((p) => [p.slug, p.status])),
  };
  write(s);
  return s;
}

export function endSession(): MockSession | null {
  const s = read();
  if (!s || s.endedAt) return s;
  const done = { ...s, endedAt: Math.min(Date.now(), s.startedAt + s.durationSec * 1000) };
  try {
    const past = JSON.parse(localStorage.getItem(HISTORY) ?? "[]") as MockSession[];
    localStorage.setItem(HISTORY, JSON.stringify([done, ...past].slice(0, 10)));
  } catch { /* history is a convenience */ }
  write(done);
  return done;
}

export function clearSession() { write(null); }
export function history(): MockSession[] {
  try { return JSON.parse(localStorage.getItem(HISTORY) ?? "[]") as MockSession[]; } catch { return []; }
}

export const clock = (secs: number) => {
  const s = Math.max(0, Math.floor(secs));
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
};

/** Live view of the current session: remaining seconds, whether it is running, and whether a problem is locked. */
export function useMock() {
  const [session, setSession] = useState<MockSession | null>(null);
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const sync = () => setSession(read());
    sync();
    window.addEventListener(EVENT, sync); window.addEventListener("storage", sync);
    return () => { window.removeEventListener(EVENT, sync); window.removeEventListener("storage", sync); };
  }, []);
  const running = !!session && !session.endedAt;
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [running]);
  const remaining = session && running ? Math.max(0, session.durationSec - (now - session.startedAt) / 1000) : 0;
  useEffect(() => { if (running && remaining <= 0) endSession(); }, [running, remaining]);
  const locked = useCallback((slug: string) => running && !!session?.slugs.includes(slug), [running, session]);
  return { session, running, remaining, locked };
}
