"use client";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type Page } from "@/lib/api";
import Skeleton from "@/components/Skeleton";
import { daysUntil, dueAt, loadReviews, markReviewed, ReviewState, STEPS } from "@/lib/review";

interface Item { id: number; slug: string; title: string; verdict: string; createdAt: string }
interface Row { slug: string; title: string; firstSolve: string }

async function loadAccepted(): Promise<Item[]> {
  const out: Item[] = [];
  for (let page = 0; page < 20; page++) {
    const d = await api<Page<Item>>(`/api/submissions?verdict=ACCEPTED&page=${page}&size=100`);
    out.push(...d.items);
    if (page + 1 >= d.totalPages) break;
  }
  return out;
}

/** Solved problems come back for review after 1, 3, 7, 14, 30 and 60 days; forgetting one restarts its schedule. */
export default function ReviewPage() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [states, setStates] = useState<Record<string, ReviewState>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    setStates(loadReviews());
    loadAccepted().then((items) => {
      const first = new Map<string, Row>();
      for (const i of items) { // newest first, so keep overwriting to end on the oldest accepted solve
        if (i.slug) first.set(i.slug, { slug: i.slug, title: i.title, firstSolve: i.createdAt });
      }
      setRows([...first.values()]);
    }).catch((e: Error) => setError(e.message));
  }, []);

  const done = useCallback((r: Row, remembered: boolean) => {
    markReviewed(r.slug, remembered, r.firstSolve);
    setStates(loadReviews());
  }, []);

  const view = useMemo(() => {
    if (!rows) return null;
    const now = Date.now();
    const list = rows.map((r) => ({ r, due: dueAt(r.firstSolve, states[r.slug]), stage: states[r.slug]?.stage ?? 0 }))
      .sort((a, b) => a.due - b.due);
    return { due: list.filter((x) => x.due <= now), later: list.filter((x) => x.due > now) };
  }, [rows, states]);

  if (error) return <div className="banner err">{error}</div>;
  if (!view) return <Skeleton lines={6} />;
  return (
    <>
      <div className="bar" style={{ marginBottom: 10 }}>
        <h2 style={{ margin: 0 }}>Review queue</h2><span className="grow" />
        <Link href="/for-you">For you</Link> · <Link href="/stats">My stats</Link>
      </div>
      <p className="mute" style={{ marginTop: 0 }}>
        Re-solve a problem from scratch, then mark whether you remembered it. Intervals: {STEPS.join(" → ")} days. Progress is kept on this device.
      </p>
      <h3>Due now ({view.due.length})</h3>
      {view.due.length === 0 && <p className="mute">Nothing due. Solve more problems and they show up here a day later.</p>}
      {view.due.map(({ r, stage }) => (
        <div key={r.slug} className="card revrow">
          <Link href={`/problems/${r.slug}`} className="grow"><b style={{ display: "inline", fontSize: 15 }}>{r.title}</b>
            <span className="mute" style={{ fontSize: 12 }}> · review #{stage + 1}</span></Link>
          <button onClick={() => done(r, true)}>Remembered</button>
          <button onClick={() => done(r, false)}>Forgot</button>
        </div>
      ))}
      <h3 style={{ marginTop: 18 }}>Coming up ({view.later.length})</h3>
      {view.later.slice(0, 30).map(({ r, due }) => (
        <div key={r.slug} className="recentrow">
          <Link href={`/problems/${r.slug}`}>{r.title}</Link><span className="grow" />
          <span className="mute" style={{ fontSize: 13 }}>in {daysUntil(due)} day{daysUntil(due) === 1 ? "" : "s"}</span>
        </div>
      ))}
    </>
  );
}
