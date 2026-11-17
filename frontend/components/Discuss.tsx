"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";

interface CommentView {
  id: number; parentId: number | null; author: string; body: string; createdAt: string;
  score: number; voted: boolean; mine: boolean;
}

const MAX = 2000;

function ago(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

/** Discussion thread for one problem: comments, one level of replies, upvotes, delete-own. */
export default function Discuss({ slug }: { slug: string }) {
  const [items, setItems] = useState<CommentView[] | null>(null);
  const [sort, setSort] = useState<"top" | "new">("top");
  const [draft, setDraft] = useState("");
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [reply, setReply] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    api<CommentView[]>(`/api/problems/${slug}/comments?sort=${sort}`)
      .then((c) => { setItems(c); setError(""); })
      .catch((e: Error) => setError(e.message));
  }, [slug, sort]);
  useEffect(() => { setItems(null); load(); }, [load]);

  const submit = useCallback(async (body: string, parentId: number | null) => {
    if (busy || !body.trim()) return;
    setBusy(true); setError("");
    try {
      await api(`/api/problems/${slug}/comments`, { method: "POST", body: JSON.stringify({ body, parentId }) });
      if (parentId == null) setDraft(""); else { setReply(""); setReplyTo(null); }
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }, [busy, slug, load]);

  const toggleVote = useCallback(async (c: CommentView) => {
    try {
      await api(`/api/comments/${c.id}/vote`, { method: c.voted ? "DELETE" : "PUT" });
      load();
    } catch (e) { setError((e as Error).message); }
  }, [load]);

  const remove = useCallback(async (c: CommentView) => {
    if (!window.confirm(c.parentId == null ? "Delete this comment and its replies?" : "Delete this reply?")) return;
    try { await api(`/api/comments/${c.id}`, { method: "DELETE" }); load(); }
    catch (e) { setError((e as Error).message); }
  }, [load]);

  const threads = useMemo(() => (items ?? []).filter((c) => c.parentId == null), [items]);
  const repliesOf = useCallback((id: number) => (items ?? []).filter((c) => c.parentId === id), [items]);

  const row = (c: CommentView, nested: boolean) => (
    <div className={`comment${nested ? " nested" : ""}`} key={c.id}>
      <div className="chead"><b>{c.author}</b>{c.mine && <span className="pill MEDIUM">you</span>}<span className="mute"> · {ago(c.createdAt)}</span></div>
      <div className="cbody">{c.body}</div>
      <div className="cactions">
        <button className={c.voted ? "on" : ""} onClick={() => toggleVote(c)} aria-pressed={c.voted}
          title={c.voted ? "Remove your upvote" : "Upvote"}>▲ {c.score}</button>
        {!nested && <button onClick={() => { setReplyTo(replyTo === c.id ? null : c.id); setReply(""); }}>Reply</button>}
        {c.mine && <button onClick={() => remove(c)}>Delete</button>}
      </div>
      {!nested && replyTo === c.id && (
        <div className="reply-box">
          <textarea value={reply} maxLength={MAX} placeholder="Write a reply…" onChange={(e) => setReply(e.target.value)} />
          <div className="bar"><span className="grow" />
            <button onClick={() => setReplyTo(null)}>Cancel</button>
            <button className="primary" disabled={busy || !reply.trim()} onClick={() => submit(reply, c.id)}>Reply</button>
          </div>
        </div>
      )}
      {!nested && repliesOf(c.id).map((r) => row(r, true))}
    </div>
  );

  return (
    <div className="discuss">
      <div className="reply-box">
        <textarea value={draft} maxLength={MAX} placeholder="Share your approach, a hint, or a question…" onChange={(e) => setDraft(e.target.value)} />
        <div className="bar">
          <span className="mute">{draft.length}/{MAX}</span><span className="grow" />
          <button className="primary" disabled={busy || !draft.trim()} onClick={() => submit(draft, null)}>Post</button>
        </div>
      </div>
      {error && <div className="banner err" style={{ margin: "8px 0" }}>{error}</div>}
      <div className="bar" style={{ margin: "10px 0 4px" }}>
        <b>{items ? `${items.length} comment${items.length === 1 ? "" : "s"}` : "Comments"}</b><span className="grow" />
        <button className={sort === "top" ? "on" : ""} onClick={() => setSort("top")}>Most votes</button>
        <button className={sort === "new" ? "on" : ""} onClick={() => setSort("new")}>Newest</button>
      </div>
      {items === null && !error && <p className="mute">Loading…</p>}
      {items !== null && threads.length === 0 && <p className="mute">No comments yet. Start the discussion.</p>}
      {threads.map((c) => row(c, false))}
    </div>
  );
}
