"use client";
import Markdown from "react-markdown";
import { useCallback, useEffect, useState } from "react";
import OfficialSolution from "@/components/OfficialSolution";
import { api } from "@/lib/api";

interface Summary {
  id: number; title: string; author: string; language: string | null; excerpt: string; createdAt: string;
  score: number; voted: boolean; mine: boolean;
}
interface Detail extends Omit<Summary, "excerpt"> { slug: string; body: string; updatedAt: string }
type View = { kind: "list" } | { kind: "open"; id: number } | { kind: "write"; edit?: Detail };

const MAX_TITLE = 120, MAX_BODY = 20000;
const LANGS = ["C++", "Java", "Python", "JavaScript", "Other"];

function ago(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

/** Community solutions for one problem (LeetCode's "Solutions" tab): list, read, write/edit, upvote, delete-own. */
export default function Solutions({ slug }: { slug: string }) {
  const [view, setView] = useState<View>({ kind: "list" });
  if (view.kind === "write") return <Write slug={slug} edit={view.edit} onDone={(id) => setView(id ? { kind: "open", id } : { kind: "list" })} />;
  if (view.kind === "open") return <Open id={view.id} onBack={() => setView({ kind: "list" })} onEdit={(d) => setView({ kind: "write", edit: d })} />;
  return <List slug={slug} onOpen={(id) => setView({ kind: "open", id })} onWrite={() => setView({ kind: "write" })} />;
}

function List({ slug, onOpen, onWrite }: { slug: string; onOpen: (id: number) => void; onWrite: () => void }) {
  const [items, setItems] = useState<Summary[] | null>(null);
  const [sort, setSort] = useState<"top" | "new">("top");
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [langFilter, setLangFilter] = useState("");
  const load = useCallback(() => {
    api<Summary[]>(`/api/problems/${slug}/solution-posts?sort=${sort}`)
      .then((r) => { setItems(r); setError(""); })
      .catch((e: Error) => setError(e.message));
  }, [slug, sort]);
  useEffect(() => { setItems(null); load(); }, [load]);
  useEffect(() => { setQ(""); setLangFilter(""); }, [slug]);

  const langs = [...new Set((items ?? []).map((s) => s.language).filter((l): l is string => !!l))];
  const needle = q.trim().toLowerCase();
  const shown = (items ?? []).filter((s) =>
    (!langFilter || s.language === langFilter) &&
    (!needle || `${s.title} ${s.author} ${s.excerpt} ${s.language ?? ""}`.toLowerCase().includes(needle)));

  return (
    <div className="discuss">
      <div className="bar" style={{ margin: "0 0 8px" }}>
        <b>{items ? `${items.length} solution${items.length === 1 ? "" : "s"}` : "Solutions"}</b><span className="grow" />
        <button className={sort === "top" ? "on" : ""} onClick={() => setSort("top")}>Most votes</button>
        <button className={sort === "new" ? "on" : ""} onClick={() => setSort("new")}>Newest</button>
        <button className="primary" onClick={onWrite}>Write a solution</button>
      </div>
      {items !== null && items.length > 0 && (
        <div className="solfilters">
          <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search solutions" aria-label="Search solutions" />
          {langs.length > 1 && (
            <div className="casechips">
              <button className={langFilter === "" ? "on" : ""} onClick={() => setLangFilter("")}>All</button>
              {langs.map((l) => <button key={l} className={langFilter === l ? "on" : ""} onClick={() => setLangFilter(l)}>{l}</button>)}
            </div>
          )}
        </div>
      )}
      <OfficialSolution slug={slug} />
      {error && <div className="banner err" style={{ margin: "8px 0" }}>{error}</div>}
      {items === null && !error && <p className="mute">Loading…</p>}
      {items !== null && items.length === 0 && <p className="mute">No community solutions yet. Be the first to share one.</p>}
      {items !== null && items.length > 0 && shown.length === 0 && <p className="mute">No solutions match your search.</p>}
      {shown.map((s) => (
        <div key={s.id} className="solrow" role="button" tabIndex={0} onClick={() => onOpen(s.id)}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onOpen(s.id); } }}>
          <div className="soltitle">{s.title}</div>
          <div className="mute solmeta">
            <b>{s.author}</b>{s.mine && <span className="pill MEDIUM">you</span>} · {ago(s.createdAt)}
            {s.language && <span className="pill">{s.language}</span>}
          </div>
          <div className="mute solexcerpt">{s.excerpt}</div>
          <div className="mute solscore">▲ {s.score}</div>
        </div>
      ))}
    </div>
  );
}

function Open({ id, onBack, onEdit }: { id: number; onBack: () => void; onEdit: (d: Detail) => void }) {
  const [d, setD] = useState<Detail | null>(null);
  const [error, setError] = useState("");
  const load = useCallback(() => {
    api<Detail>(`/api/solution-posts/${id}`).then((r) => { setD(r); setError(""); }).catch((e: Error) => setError(e.message));
  }, [id]);
  useEffect(() => { load(); }, [load]);

  const vote = async () => {
    if (!d) return;
    try { await api(`/api/solution-posts/${id}/vote`, { method: d.voted ? "DELETE" : "PUT" }); load(); }
    catch (e) { setError((e as Error).message); }
  };
  const remove = async () => {
    if (!window.confirm("Delete this solution?")) return;
    try { await api(`/api/solution-posts/${id}`, { method: "DELETE" }); onBack(); }
    catch (e) { setError((e as Error).message); }
  };

  return (
    <div className="discuss">
      <div className="bar" style={{ margin: "0 0 8px" }}><button className="backbtn" onClick={onBack}>← All solutions</button></div>
      {error && <div className="banner err" style={{ margin: "8px 0" }}>{error}</div>}
      {!d && !error && <p className="mute">Loading…</p>}
      {d && (
        <>
          <h3 style={{ margin: "4px 0" }}>{d.title}</h3>
          <div className="mute solmeta">
            <b>{d.author}</b>{d.mine && <span className="pill MEDIUM">you</span>} · {ago(d.createdAt)}
            {d.updatedAt !== d.createdAt && " (edited)"}
            {d.language && <span className="pill">{d.language}</span>}
          </div>
          <div className="cbody md" style={{ marginTop: 12 }}><Markdown>{d.body}</Markdown></div>
          <div className="cactions" style={{ marginTop: 12 }}>
            <button className={d.voted ? "on" : ""} onClick={vote} aria-pressed={d.voted} title={d.voted ? "Remove your upvote" : "Upvote"}>▲ {d.score}</button>
            {d.mine && <button onClick={() => onEdit(d)}>Edit</button>}
            {d.mine && <button onClick={remove}>Delete</button>}
          </div>
        </>
      )}
    </div>
  );
}

function Write({ slug, edit, onDone }: { slug: string; edit?: Detail; onDone: (id: number | null) => void }) {
  const [title, setTitle] = useState(edit?.title ?? "");
  const [body, setBody] = useState(edit?.body ?? "");
  const [language, setLanguage] = useState(edit?.language ?? "");
  const [preview, setPreview] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    if (busy) return;
    setBusy(true); setError("");
    try {
      const payload = JSON.stringify({ title, body, language });
      const saved = edit
        ? await api<Detail>(`/api/solution-posts/${edit.id}`, { method: "PUT", body: payload })
        : await api<Detail>(`/api/problems/${slug}/solution-posts`, { method: "POST", body: payload });
      onDone(saved.id);
    } catch (e) { setError((e as Error).message); setBusy(false); }
  };

  return (
    <div className="discuss">
      <div className="bar" style={{ margin: "0 0 8px" }}>
        <button className="backbtn" onClick={() => onDone(edit ? edit.id : null)}>← Cancel</button><span className="grow" />
        <button className={preview ? "on" : ""} onClick={() => setPreview(!preview)}>{preview ? "Edit" : "Preview"}</button>
      </div>
      <input value={title} maxLength={MAX_TITLE} placeholder="Title, e.g. “One pass with a hash map”" onChange={(e) => setTitle(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
      <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ marginBottom: 8 }} aria-label="Language">
        <option value="">Language (optional)</option>
        {LANGS.map((l) => <option key={l} value={l}>{l}</option>)}
      </select>
      {preview
        ? <div className="cbody md reply-box"><Markdown>{body || "*Nothing to preview yet.*"}</Markdown></div>
        : <textarea className="solbody" value={body} maxLength={MAX_BODY} rows={14} onChange={(e) => setBody(e.target.value)}
            placeholder={"Explain your approach, then add code in ``` fences. Markdown works."} />}
      {error && <div className="banner err" style={{ margin: "8px 0" }}>{error}</div>}
      <div className="bar">
        <span className="mute">{body.length}/{MAX_BODY}</span><span className="grow" />
        <button className="primary" disabled={busy || !title.trim() || body.trim().length < 10} onClick={submit}>{edit ? "Save" : "Publish"}</button>
      </div>
    </div>
  );
}
