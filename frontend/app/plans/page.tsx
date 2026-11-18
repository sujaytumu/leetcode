"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Plan } from "@/lib/api";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" } as const;

export default function PlansPage() {
  usePageTitle("Study plans");
  const [plans, setPlans] = useState<Plan[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    swr<Plan[]>("/api/plans", (d) => setPlans(d), () => {}).catch((e) => setError(e.message));
  }, []);

  return (
    <>
      <h2 style={{ marginTop: 0 }}>Study plans</h2>
      {error && <div className="banner err">{error}</div>}
      {!plans && !error && <Skeleton lines={8} />}
      <div className="plans">
        {plans?.map((plan) => {
          const pct = Math.round((plan.solved / plan.total) * 100);
          return (
            <details key={plan.id} className="plan">
              <summary>
                <div className="bar"><b>{plan.title}</b><span className="grow" /><span className="mute">{plan.solved}/{plan.total}</span></div>
                <div className="mute" style={{ fontSize: 13 }}>{plan.blurb}</div>
                <div className="progress"><div style={{ width: `${pct}%` }} /></div>
                {(() => {
                  const next = plan.problems.find((p) => p.status !== "SOLVED");
                  return next
                    ? <div style={{ marginTop: 8, fontSize: 13 }}>
                        <Link href={`/problems/${next.slug}`} onClick={(e) => e.stopPropagation()}>
                          {plan.solved === 0 ? "Start" : "Continue"}: <b style={{ display: "inline", fontSize: 13 }}>{next.title}</b> →
                        </Link>
                      </div>
                    : <div className="EASY" style={{ marginTop: 8, fontSize: 13 }}>Plan complete 🎉</div>;
                })()}
              </summary>
              <ul>
                {plan.problems.map((p) => (
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
