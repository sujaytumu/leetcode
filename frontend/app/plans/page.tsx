"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ProblemSummary } from "@/lib/api";
import { loadAll } from "@/lib/local";
import { inPlan, PLANS } from "@/lib/plans";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" } as const;

export default function PlansPage() {
  const [all, setAll] = useState<ProblemSummary[]>([]);
  const [saved, setSaved] = useState(false);
  const [waking, setWaking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAll((items, fromCache) => { setAll(items); setSaved(fromCache); }, () => setWaking(true))
      .then(() => setWaking(false))
      .catch((e) => { setError(e.message); setWaking(false); });
  }, []);

  return (
    <>
      <h2 style={{ marginTop: 0 }}>Study plans</h2>
      {saved && !error && <div className="banner warn">Showing a saved copy{waking ? " while the server wakes up (1–3 min) — refreshing automatically…" : "."}</div>}
      {error && <div className="banner err">{error}</div>}
      {!all.length && !error && <p className="mute">Loading…</p>}
      <div className="plans">
        {all.length > 0 && PLANS.map((plan) => {
          const items = inPlan(plan, all);
          if (!items.length) return null;
          const solved = items.filter((p) => p.status === "SOLVED").length;
          const pct = Math.round((solved / items.length) * 100);
          return (
            <details key={plan.id} className="plan">
              <summary>
                <div className="bar"><b>{plan.title}</b><span className="grow" /><span className="mute">{solved}/{items.length}</span></div>
                <div className="mute" style={{ fontSize: 13 }}>{plan.blurb}</div>
                <div className="progress"><div style={{ width: `${pct}%` }} /></div>
              </summary>
              <ul>
                {items.map((p) => (
                  <li key={p.id}>
                    <span className={p.status === "SOLVED" ? "EASY" : "mute"}>{ICON[p.status]}</span>{" "}
                    <Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}</Link>{" "}
                    <span className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
                  </li>
                ))}
              </ul>
            </details>
          );
        })}
      </div>
    </>
  );
}
