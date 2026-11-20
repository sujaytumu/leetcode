"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Plan } from "@/lib/api";
import { swr } from "@/lib/local";
import { bannerFor, planLevel } from "@/lib/planMeta";

/** Row of study-plan cards above the problem table (LeetCode's problemset header). Hidden on phones. */
export default function PlanStrip() {
  const [plans, setPlans] = useState<Plan[] | null>(null);
  useEffect(() => { swr<Plan[]>("/api/plans", (d) => setPlans(d), () => {}).catch(() => setPlans([])); }, []);
  if (!plans || plans.length === 0) return null;
  return (
    <div className="planstrip">
      {plans.slice(0, 4).map((p) => {
        const pct = p.total ? Math.round((p.solved / p.total) * 100) : 0;
        const [c1, c2] = bannerFor(p.id);
        const next = p.problems.find((x) => x.status !== "SOLVED");
        return (
          <Link key={p.id} href={next && pct > 0 ? `/problems/${next.slug}` : "/plans"} className="pscard" style={{ background: `linear-gradient(135deg, ${c1}, ${c2})` }}>
            <span className="pslevel">{planLevel(p.problems)}</span>
            <b>{p.title}</b>
            <span className="psmeta">{p.solved}/{p.total} solved</span>
            <span className="psbar"><i style={{ width: `${pct}%` }} /></span>
          </Link>
        );
      })}
      <Link href="/plans" className="psall">All study plans →</Link>
    </div>
  );
}
