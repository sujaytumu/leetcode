"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { type ListSummary, MAX_LISTS } from "@/lib/lists";

/** "Add to list" button with a small checklist popover, like LeetCode's list picker. */
export default function AddToList({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [lists, setLists] = useState<ListSummary[] | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  const load = useCallback(() => {
    api<ListSummary[]>(`/api/lists?slug=${encodeURIComponent(slug)}`).then(setLists).catch((e) => setError((e as Error).message));
  }, [slug]);

  useEffect(() => { if (open) { setError(""); load(); } }, [open, load]);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (box.current && !box.current.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away); document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", esc); };
  }, [open]);

  async function toggle(l: ListSummary) {
    setBusy(true); setError("");
    try {
      await api(`/api/lists/${l.id}/problems/${slug}`, { method: l.contains ? "DELETE" : "PUT" });
      setLists((cur) => cur?.map((x) => x.id === l.id ? { ...x, contains: !l.contains, count: x.count + (l.contains ? -1 : 1) } : x) ?? cur);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  async function create(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true); setError("");
    try {
      const made = await api<ListSummary>("/api/lists", { method: "POST", body: JSON.stringify({ name }) });
      await api(`/api/lists/${made.id}/problems/${slug}`, { method: "PUT" });
      setName(""); load();
    } catch (err) { setError((err as Error).message); } finally { setBusy(false); }
  }

  const inAny = lists?.some((l) => l.contains);
  return (
    <div className="addlist" ref={box}>
      <button onClick={() => setOpen((o) => !o)} aria-haspopup="true" aria-expanded={open} title="Add to one of your lists"
        style={inAny ? { color: "var(--accent)" } : undefined}>☰ List</button>
      {open && (
        <div className="addlist-pop" role="dialog" aria-label="Add to list">
          <div className="addlist-head"><b>Add to list</b><Link href="/lists" className="mute">Manage</Link></div>
          {!lists && !error && <div className="mute">Loading…</div>}
          {lists && lists.length === 0 && <div className="mute" style={{ marginBottom: 8 }}>No lists yet — create your first one.</div>}
          <ul>
            {lists?.map((l) => (
              <li key={l.id}>
                <label><input type="checkbox" checked={l.contains} disabled={busy} onChange={() => toggle(l)} /> {l.name}</label>
                <span className="mute">{l.count}</span>
              </li>
            ))}
          </ul>
          {error && <div className="EASY" style={{ color: "var(--hard)", fontSize: 12, margin: "6px 0" }}>{error}</div>}
          {(lists?.length ?? 0) < MAX_LISTS && (
            <form onSubmit={create} className="addlist-new">
              <input value={name} maxLength={60} onChange={(e) => setName(e.target.value)} placeholder="New list name" aria-label="New list name" />
              <button disabled={busy || !name.trim()}>Create</button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
