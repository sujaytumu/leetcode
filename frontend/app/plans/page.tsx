"use client";
import Link from "next/link";
import { useCatalog } from "@/lib/catalog";
import { inPlan, PLANS } from "@/lib/plans";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" } as const;

export default function PlansPage() {
  const { items: all, ready, server, retry, loadError: error } = useCatalog();

  return (
    <main className="page">
      <h2 style={{ marginTop: 0 }}>Study plans</h2>
      {server === "offline" && <div className="banner warn">The server is not responding, so solved status may be out of date. <button onClick={retry}>Retry</button></div>}
      {error && <div className="banner err">{error}</div>}
      {!ready && !error && <p className="mute">Loading…</p>}
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
                    <Link href={`/problems/${p.slug}`}>{p.id}. {p.title}</Link>{" "}
                    <span className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
                  </li>
                ))}
              </ul>
            </details>
          );
        })}
      </div>
    </main>
  );
}
