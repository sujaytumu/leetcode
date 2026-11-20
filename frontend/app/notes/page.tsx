"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { loadAll } from "@/lib/local";
import { filterNotes, listNotes, NoteEntry, toMarkdown } from "@/lib/notes";
import { usePageTitle } from "@/lib/usePageTitle";

/** Every note you wrote in the problem workspace, searchable, with a Markdown export. */
export default function NotesPage() {
  usePageTitle("My notes");
  const [notes, setNotes] = useState<NoteEntry[] | null>(null);
  const [titles, setTitles] = useState<Map<string, string>>(new Map());
  const [q, setQ] = useState("");

  useEffect(() => {
    setNotes(listNotes(localStorage));
    loadAll((items) => setTitles(new Map(items.map((p) => [p.slug, p.title]))), () => {}).catch(() => {});
  }, []);

  const shown = useMemo(() => (notes ? filterNotes(notes, q, titles) : []), [notes, q, titles]);

  function exportAll() {
    const blob = new Blob([toMarkdown(shown, titles)], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "my-leetcode-notes.md"; a.click();
    URL.revokeObjectURL(a.href);
  }

  if (!notes) return null;
  return (
    <>
      <div className="bar" style={{ marginBottom: 10 }}>
        <h2 style={{ margin: 0 }}>My notes</h2><span className="grow" />
        <button onClick={exportAll} disabled={!shown.length}>Export Markdown</button>
      </div>
      <input placeholder="Search notes…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search notes" style={{ width: "100%", marginBottom: 12 }} />
      {notes.length === 0 && <p className="mute">No notes yet. Open any problem and use the Notes box under the description.</p>}
      {notes.length > 0 && shown.length === 0 && <p className="mute">No notes match “{q}”.</p>}
      {shown.map((n) => (
        <section key={n.slug} className="card" style={{ marginBottom: 10 }}>
          <div className="bar">
            <Link href={`/problems/${n.slug}`}><b style={{ display: "inline", fontSize: 15 }}>{titles.get(n.slug) ?? n.slug}</b></Link>
            <span className="grow" />
            {n.updatedAt > 0 && <span className="mute" style={{ fontSize: 12 }}>{new Date(n.updatedAt).toLocaleDateString()}</span>}
          </div>
          <pre className="notebody">{n.text}</pre>
        </section>
      ))}
    </>
  );
}
