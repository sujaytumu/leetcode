"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, Profile } from "@/lib/api";
import type { ListDetail, ListSummary } from "@/lib/lists";

type Tab = "recent" | "list" | "solutions";

function ago(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  const unit = (n: number, name: string) => (n === 1 ? `a ${name} ago` : `${n} ${name}s ago`);
  if (s < 60) return "just now";
  if (s < 3600) return unit(Math.floor(s / 60), "minute");
  if (s < 86400) return unit(Math.floor(s / 3600), "hour");
  if (s < 86400 * 30) return unit(Math.floor(s / 86400), "day");
  if (s < 86400 * 365) return unit(Math.floor(s / (86400 * 30)), "month");
  return unit(Math.floor(s / (86400 * 365)), "year");
}

/** LeetCode's profile tabs: Recent AC, List (your own lists; private, so own page only) and Solutions. */
export default function ProfileTabs({ p, own }: { p: Profile; own: boolean }) {
  const [tab, setTab] = useState<Tab>("recent");
  const tabs: { id: Tab; label: string }[] = [
    { id: "recent", label: "Recent AC" },
    ...(own ? [{ id: "list" as Tab, label: "List" }] : []),
    { id: "solutions", label: "Solutions" },
  ];
  return (
    <section className="card ptabs">
      <div className="ptab-bar" role="tablist">
        {tabs.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} className={tab === t.id ? "on" : ""} onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>
      {tab === "recent" && (
        <div className="prows">
          {p.recentAccepted.length === 0 && <p className="mute" style={{ padding: "8px 4px" }}>{own ? "No accepted submissions yet. Solve a problem and it shows up here." : "No accepted submissions yet."}</p>}
          {p.recentAccepted.map((r, i) => (
            <Link key={`${r.slug}-${i}`} href={`/problems/${r.slug}`} className="prow">
              <span className="prow-title">{r.title}</span>
              <span className="grow" />
              <span className="mute prow-when">{ago(r.at)}</span>
            </Link>
          ))}
        </div>
      )}
      {tab === "list" && own && <Lists />}
      {tab === "solutions" && (
        <div className="prows">
          <p className="mute" style={{ padding: "8px 4px" }}>
            {(p.community?.solutions ?? 0) > 0
              ? `${p.community?.solutions} community solution${p.community?.solutions === 1 ? "" : "s"} posted. Open a problem's Solutions tab to read or edit them.`
              : "No community solutions yet. Share one from any problem's Solutions tab."}
          </p>
        </div>
      )}
    </section>
  );
}

function Lists() {
  const [lists, setLists] = useState<ListDetail[] | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let live = true;
    api<ListSummary[]>("/api/lists")
      .then((ls) => Promise.all(ls.map((l) => api<ListDetail>(`/api/lists/${l.id}`))))
      .then((d) => { if (live) setLists(d); })
      .catch((e: Error) => { if (live) setError(e.message); });
    return () => { live = false; };
  }, []);
  if (error) return <div className="banner err">{error}</div>;
  if (!lists) return <p className="mute" style={{ padding: "8px 4px" }}>Loading…</p>;
  if (lists.length === 0) return <p className="mute" style={{ padding: "8px 4px" }}>No lists yet. <Link href="/lists">Create one</Link> and add problems to it.</p>;
  return (
    <div className="prows">
      {lists.map((l) => (
        <details key={l.id} className="plist">
          <summary className="prow"><span className="prow-title">{l.name}</span><span className="grow" /><span className="mute prow-when">{l.problems.length} problem{l.problems.length === 1 ? "" : "s"}</span></summary>
          <div className="plist-items">
            {l.problems.length === 0 && <span className="mute">Empty list.</span>}
            {l.problems.map((x) => (
              <Link key={x.slug} href={`/problems/${x.slug}`} className="plist-item">
                <span>{x.title}</span><span className="grow" />
                <span className={x.difficulty} style={{ fontSize: 12 }}>{x.difficulty[0] + x.difficulty.slice(1).toLowerCase()}</span>
              </Link>
            ))}
          </div>
        </details>
      ))}
    </div>
  );
}
