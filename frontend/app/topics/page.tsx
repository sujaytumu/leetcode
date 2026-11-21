"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import Skeleton from "@/components/Skeleton";
import { Topic, tagLabel } from "@/lib/api";
import { swr } from "@/lib/local";
import { useMeta } from "@/lib/meta";

export default function TopicsPage() {
  usePageTitle("Topics");
  const meta = useMeta();
  const [topics, setTopics] = useState<Topic[] | null>(null);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"default" | "least" | "most">("default");

  useEffect(() => { swr<Topic[]>("/api/topics", (d) => setTopics(d), () => {}).catch((e) => setError(e.message)); }, []);

  const pctOf = (t: Topic) => (t.total ? t.solved / t.total : 0);
  const shown = topics?.filter((t) => tagLabel(t.tag).toLowerCase().includes(q.trim().toLowerCase()))
    .sort((a, b) => (sort === "least" ? pctOf(a) - pctOf(b) : sort === "most" ? pctOf(b) - pctOf(a) : 0));
  // Weakest = lowest solved share among topics big enough to matter; ties go to the larger topic.
  const weakest = topics?.filter((t) => t.total >= 3 && t.solved < t.total)
    .sort((a, b) => pctOf(a) - pctOf(b) || b.total - a.total)[0];
  return (
    <>
      <div className="bar" style={{ marginBottom: 12, flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>Topics</h2><span className="grow" />
        <select aria-label="Sort topics" value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
          <option value="default">Default order</option><option value="least">Least solved first</option><option value="most">Most solved first</option>
        </select>
        <input placeholder="Filter topics…" value={q} onChange={(e) => setQ(e.target.value)} style={{ maxWidth: 240, minWidth: 0, flex: "1 1 140px" }} />
      </div>
      {error && <div className="banner err">{error}</div>}
      {weakest && (
        <div className="banner" style={{ marginBottom: 12 }}>
          <span>Weakest topic: <b>{tagLabel(weakest.tag)}</b> ({weakest.solved}/{weakest.total} solved)</span><span className="grow" />
          <Link href={`/practice?tag=${encodeURIComponent(weakest.tag)}`}>Practice it →</Link>
        </div>
      )}
      {!topics && !error && <Skeleton lines={8} />}
      <div className="topics">
        {shown?.map((t) => {
          const pct = t.total ? Math.round((t.solved / t.total) * 100) : 0;
          return (
            <Link key={t.tag} href={`/problems?tag=${encodeURIComponent(t.tag)}`} className="card topic">
              <div className="bar"><b>{tagLabel(t.tag)}</b><span className="grow" /><span className="mute">{t.solved}/{t.total}</span></div>
              <div className="progress"><div style={{ width: `${pct}%` }} /></div>
              <div className="topic-diff">
                {(meta?.difficulties ?? []).map((d) => (
                  <span key={d.key} className={d.key}>{d.label} {t.byDifficulty[d.key] ?? 0}</span>
                ))}
              </div>
            </Link>
          );
        })}
        {shown && shown.length === 0 && <p className="mute">No topics match.</p>}
      </div>
    </>
  );
}
