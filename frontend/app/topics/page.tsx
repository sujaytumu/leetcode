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

  useEffect(() => { swr<Topic[]>("/api/topics", (d) => setTopics(d), () => {}).catch((e) => setError(e.message)); }, []);

  const shown = topics?.filter((t) => tagLabel(t.tag).toLowerCase().includes(q.trim().toLowerCase()));
  return (
    <>
      <div className="bar" style={{ marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Topics</h2><span className="grow" />
        <input placeholder="Filter topics…" value={q} onChange={(e) => setQ(e.target.value)} style={{ maxWidth: 240 }} />
      </div>
      {error && <div className="banner err">{error}</div>}
      {!topics && !error && <Skeleton lines={8} />}
      <div className="topics">
        {shown?.map((t) => {
          const pct = t.total ? Math.round((t.solved / t.total) * 100) : 0;
          return (
            <Link key={t.tag} href={`/?tag=${encodeURIComponent(t.tag)}`} className="card topic">
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
