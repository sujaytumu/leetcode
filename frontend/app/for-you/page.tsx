"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import Skeleton from "@/components/Skeleton";
import { Recommendation, Recommendations } from "@/lib/api";
import { swr } from "@/lib/local";

function Section({ title, blurb, items }: { title: string; blurb: string; items: Recommendation[] }) {
  if (items.length === 0) return null;
  return (
    <section style={{ marginBottom: 24 }}>
      <h3 style={{ margin: "0 0 2px" }}>{title}</h3>
      <p className="mute" style={{ margin: "0 0 10px", fontSize: 13 }}>{blurb}</p>
      <div className="recs">
        {items.map(({ problem: p, reason }) => (
          <Link key={p.id} href={`/problems/${p.slug}`} className="card rec">
            <div className="bar">
              <b>{p.number ?? p.id}. {p.title}</b><span className="grow" />
              <span className={p.difficulty} style={{ fontSize: 12 }}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
            </div>
            <div className="mute" style={{ fontSize: 13, marginTop: 6 }}>{reason}</div>
          </Link>
        ))}
      </div>
    </section>
  );
}

export default function ForYouPage() {
  usePageTitle("For you");
  const [data, setData] = useState<Recommendations | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { swr<Recommendations>("/api/recommendations", (d) => setData(d), () => {}).catch((e) => setError(e.message)); }, []);

  const empty = data && !data.next.length && !data.unfinished.length && !data.revisit.length;
  return (
    <>
      <h2 style={{ marginTop: 0 }}>For you</h2>
      {error && <div className="banner err">{error}</div>}
      {!data && !error && <Skeleton lines={9} />}
      {data && (
        <>
          <Section title="Pick up where you left off" blurb="You tried these but haven't got an accepted solution yet." items={data.unfinished} />
          <Section title="Up next" blurb="Chosen from topics you're partway through, at a difficulty that fits your progress." items={data.next} />
          <Section title="Time to revisit" blurb="Solved a while ago. A quick second pass makes it stick." items={data.revisit} />
          {empty && <p className="mute">Nothing to recommend right now. Solve a few problems and suggestions will show up here.</p>}
        </>
      )}
    </>
  );
}
