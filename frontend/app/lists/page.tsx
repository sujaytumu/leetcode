"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type Status } from "@/lib/api";
import { type ListDetail, type ListSummary, MAX_LISTS } from "@/lib/lists";
import Skeleton from "@/components/Skeleton";
import { cacheGet, cacheSet } from "@/lib/local";

const ICON: Record<Status, string> = { SOLVED: "✔", ATTEMPTED: "◐", TODO: "○" };

function ListCard({ list, onChange }: { list: ListSummary; onChange: () => void }) {
  const [open, setOpen] = useState(false);
  const [detail, setDetail] = useState<ListDetail | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    const path = `/api/lists/${list.id}`;
    setDetail((d) => d ?? cacheGet<ListDetail>(path));
    api<ListDetail>(path).then((d) => { cacheSet(path, d); setDetail(d); }).catch((e) => setError((e as Error).message));
  }, [list.id]);
  useEffect(() => { if (open) load(); }, [open, load, list.count]);

  async function remove(slug: string) {
    try { await api(`/api/lists/${list.id}/problems/${slug}`, { method: "DELETE" }); load(); onChange(); }
    catch (e) { setError((e as Error).message); }
  }
  async function destroy() {
    if (!confirm(`Delete the list "${list.name}"? Your problems are not affected.`)) return;
    try { await api(`/api/lists/${list.id}`, { method: "DELETE" }); onChange(); } catch (e) { setError((e as Error).message); }
  }

  const solved = detail?.problems.filter((p) => p.status === "SOLVED").length ?? 0;
  return (
    <details className="plan" open={open} onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}>
      <summary>
        <div className="bar"><b>{list.name}</b><span className="grow" />
          <span className="mute">{detail ? `${solved}/${detail.problems.length} solved` : `${list.count} problem${list.count === 1 ? "" : "s"}`}</span></div>
        {detail && detail.problems.length > 0 && <div className="progress"><div style={{ width: `${Math.round((solved / detail.problems.length) * 100)}%` }} /></div>}
      </summary>
      {error && <div className="banner err">{error}</div>}
      {open && !detail && !error && <Skeleton lines={3} />}
      {detail && detail.problems.length === 0 && <p className="mute">Empty. Open a problem and use <b>☰ List</b> to add it here.</p>}
      <ul>
        {detail?.problems.map((p) => (
          <li key={p.id} className="listrow">
            <span className={p.status === "SOLVED" ? "EASY" : "mute"}>{ICON[p.status]}</span>{" "}
            <Link href={`/problems/${p.slug}`}>{p.number ?? p.id}. {p.title}</Link>{" "}
            <span className={p.difficulty}>{p.difficulty[0] + p.difficulty.slice(1).toLowerCase()}</span>
            <span className="grow" />
            <button className="linklike" onClick={() => remove(p.slug)} aria-label={`Remove ${p.title} from list`}>Remove</button>
          </li>
        ))}
      </ul>
      <div style={{ marginTop: 8 }}><button onClick={destroy}>Delete list</button></div>
    </details>
  );
}

export default function ListsPage() {
  usePageTitle("Lists");
  const [lists, setLists] = useState<ListSummary[] | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setLists((l) => l ?? cacheGet<ListSummary[]>("/api/lists"));
    api<ListSummary[]>("/api/lists").then((l) => { cacheSet("/api/lists", l); setLists(l); }).catch((e) => setError((e as Error).message));
  }, []);
  useEffect(load, [load]);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try { await api("/api/lists", { method: "POST", body: JSON.stringify({ name }) }); setName(""); load(); }
    catch (err) { setError((err as Error).message); }
  }

  return (
    <>
      <span className="narrowmark" hidden />
      <h2 style={{ marginTop: 0 }}>My lists</h2>
      <form onSubmit={create} className="filters" style={{ marginBottom: 14 }}>
        <input className="grow" value={name} maxLength={60} onChange={(e) => setName(e.target.value)} placeholder="Name a new list, e.g. “Revise before interview”" aria-label="New list name" />
        <button disabled={!name.trim() || (lists?.length ?? 0) >= MAX_LISTS}>Create list</button>
      </form>
      {error && <div className="banner err">{error}</div>}
      {!lists && !error && <Skeleton lines={5} />}
      {lists && lists.length === 0 && <p className="mute">You have no lists yet. Create one above, then add problems from any problem page with <b>☰ List</b>.</p>}
      <div className="plans">{lists?.map((l) => <ListCard key={l.id} list={l} onChange={load} />)}</div>
    </>
  );
}
