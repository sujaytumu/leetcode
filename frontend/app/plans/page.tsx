"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Plan } from "@/lib/api";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";
import { bannerFor, planLevel, planState } from "@/lib/planMeta";

const ICON = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" } as const;
const cap = (d: string) => d[0] + d.slice(1).toLowerCase();

function Ring({ pct }: { pct: number }) {
  const R = 18, C = 2 * Math.PI * R;
  return (
    <svg width="46" height="46" viewBox="0 0 46 46" role="img" aria-label={`${pct}% complete`}>
      <circle cx="23" cy="23" r={R} fill="none" stroke="var(--cell)" strokeWidth="4" />
      <circle cx="23" cy="23" r={R} fill="none" stroke={pct >= 100 ? "#2cbb5d" : "var(--accent)"} strokeWidth="4" strokeLinecap="round"
        strokeDasharray={C} strokeDashoffset={C * (1 - pct / 100)} transform="rotate(-90 23 23)" />
      <text x="23" y="27" textAnchor="middle" fontSize="11" fontWeight="700" fill="var(--text)">{pct}%</text>
    </svg>
  );
}

export default function PlansPage() {
  usePageTitle("Study plans");
  const [plans, setPlans] = useState<Plan[] | null>(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    swr<Plan[]>("/api/plans", (d) => setPlans(d), () => {}).catch((e) => setError(e.message));
  }, []);

  const current = plans?.find((p) => p.id === open) ?? null;

  return (
    <>
      <span className="narrowmark" hidden />
      <h2 style={{ marginTop: 0 }}>Study Plan</h2>
      <p className="mute" style={{ marginTop: -4 }}>Follow a structured path, one problem at a time.</p>
      {error && <div className="banner err">{error}</div>}
      {!plans && !error && <Skeleton lines={8} />}
      <div className="plangrid">
        {plans?.map((plan) => {
          const pct = plan.total ? Math.round((plan.solved / plan.total) * 100) : 0;
          const [c1, c2] = bannerFor(plan.id);
          const state = planState(plan);
          const next = plan.problems.find((p) => p.status !== "SOLVED");
          return (
            <article key={plan.id} className={`plancard${open === plan.id ? " open" : ""}`}>
              <div className="planbanner" style={{ background: `linear-gradient(135deg, ${c1}, ${c2})` }}>
                <span className="planlevel">{planLevel(plan.problems)}</span>
              </div>
              <div className="planbody">
                <div className="bar" style={{ alignItems: "flex-start" }}>
                  <div className="grow">
                    <h3 style={{ margin: 0 }}>{plan.title}</h3>
                    <div className="mute" style={{ fontSize: 12, margin: "2px 0 6px" }}>{plan.total} problems · {plan.solved} solved</div>
                  </div>
                  <Ring pct={pct} />
                </div>
                <div className="mute" style={{ fontSize: 13, minHeight: 36 }}>{plan.blurb}</div>
                <div className="bar" style={{ marginTop: 10 }}>
                  {next
                    ? <Link href={`/problems/${next.slug}`} className="planbtn">{state === "start" ? "Start Learning" : "Continue"}</Link>
                    : <span className="planbtn done">Completed 🎉</span>}
                  <button type="button" onClick={() => setOpen(open === plan.id ? null : plan.id)} aria-expanded={open === plan.id}>
                    {open === plan.id ? "Hide problems" : "View problems"}
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
      {current && (
        <section className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginTop: 0 }}>{current.title}</h3>
          <ul className="planlist">
            {current.problems.map((p, i) => (
              <li key={p.id}>
                <span className="mute" style={{ width: 24, display: "inline-block" }}>{i + 1}</span>
                <span className={p.status === "SOLVED" ? "ok" : "mute"}>{ICON[p.status]}</span>{" "}
                <Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}</Link>
                <span className="grow" />
                <span className={p.difficulty}>{cap(p.difficulty)}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
