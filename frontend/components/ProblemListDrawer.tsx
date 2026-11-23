"use client";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { ProblemSummary } from "@/lib/api";
import Skeleton from "./Skeleton";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" } as const;

/** LeetCode-style "Problem List" slide-over: search, see status, jump to any problem without leaving the editor. */
export default function ProblemListDrawer({ open, onClose, problems, currentSlug }:
  { open: boolean; onClose: () => void; problems: ProblemSummary[]; currentSlug: string }) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const input = useRef<HTMLInputElement>(null);
  const current = useRef<HTMLLIElement>(null);

  useEffect(() => {
    if (!open) return;
    setQ("");
    const t = setTimeout(() => { input.current?.focus(); current.current?.scrollIntoView({ block: "center" }); }, 60);
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => { clearTimeout(t); window.removeEventListener("keydown", onKey); };
  }, [open, onClose]);

  const shown = useMemo(() => {
    const term = q.trim().toLowerCase();
    if (!term) return problems;
    return problems.filter((p) =>
      p.title.toLowerCase().includes(term) || String(p.number ?? p.id) === term || p.tags.some((t) => t.includes(term)));
  }, [problems, q]);

  if (!open) return null;
  const go = (slug: string) => { onClose(); router.push(`/problems/${slug}`); };
  const shuffle = () => {
    const pool = problems.filter((p) => p.status !== "SOLVED" && p.slug !== currentSlug);
    const pick = (pool.length ? pool : problems)[Math.floor(Math.random() * (pool.length || problems.length))];
    if (pick) go(pick.slug);
  };
  const solved = problems.filter((p) => p.status === "SOLVED").length;

  return (
    <div className="drawer-back" onClick={onClose}>
      <aside className="drawer" role="dialog" aria-label="Problem list" onClick={(e) => e.stopPropagation()}>
        <div className="bar" style={{ marginBottom: 8 }}>
          <b>Problem List</b><span className="grow" />
          <span className="mute" style={{ fontSize: 12 }}>{solved}/{problems.length} solved</span>
          <button onClick={shuffle} title="Open a random unsolved problem" aria-label="Random problem">🎲</button>
          <button onClick={onClose} aria-label="Close">✕</button>
        </div>
        <input ref={input} placeholder="Search by title, number or topic…" value={q} onChange={(e) => setQ(e.target.value)} />
        {problems.length === 0 ? <Skeleton lines={10} /> : (
          <ul className="drawer-list">
            {shown.map((p) => (
              <li key={p.id} ref={p.slug === currentSlug ? current : undefined}
                className={p.slug === currentSlug ? "on" : ""} onClick={() => go(p.slug)}>
                <span className={p.status === "SOLVED" ? "EASY" : p.status === "ATTEMPTED" ? "MEDIUM" : "mute"}>{ICON[p.status]}</span>
                <span className="drawer-title">{p.number ?? p.id}. {p.title}</span>
                <span className={p.difficulty} style={{ fontSize: 12 }}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
              </li>
            ))}
            {shown.length === 0 && <li className="mute">No problems match.</li>}
          </ul>
        )}
      </aside>
    </div>
  );
}
