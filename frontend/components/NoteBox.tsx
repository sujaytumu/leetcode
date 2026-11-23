"use client";
import { useEffect, useState } from "react";

const COLORS = ["#8a8a8a", "#ffc01e", "#2d7cf6", "#2cbb5d", "#ef4d9b", "#a855f7"];
interface Meta { tags: string[]; color: number }

/** LeetCode's note editor under a submission: text, up to 5 related tags, and a colour label. Tags/colour stay on this device. */
export default function NoteBox({ slug, value, onChange, tags }: { slug: string; value: string; onChange: (v: string) => void; tags: string[] }) {
  const key = `lc-notemeta:${slug}`;
  const [meta, setMeta] = useState<Meta>({ tags: [], color: 0 });
  const [open, setOpen] = useState(false);
  useEffect(() => { try { const m = JSON.parse(localStorage.getItem(key) || "null"); if (m) setMeta(m); else setMeta({ tags: [], color: 0 }); } catch { /* ignore */ } }, [key]);
  const save = (m: Meta) => { setMeta(m); try { localStorage.setItem(key, JSON.stringify(m)); } catch { /* ignore */ } };
  const toggle = (t: string) => save({ ...meta, tags: meta.tags.includes(t) ? meta.tags.filter((x) => x !== t) : meta.tags.length < 5 ? [...meta.tags, t] : meta.tags });
  return (
    <div className="notebox">
      <textarea placeholder="Write your notes here" aria-label="Notes for this problem" value={value} onChange={(e) => onChange(e.target.value)} />
      <div className="notefoot">
        <button type="button" className="notetags" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
          {meta.tags.length ? meta.tags.join(", ") : "Select related tags"}
        </button>
        <span className="mute">{meta.tags.length}/5</span>
      </div>
      {open && (
        <div className="notepick">
          {tags.map((t) => (
            <button key={t} type="button" className={`chip${meta.tags.includes(t) ? " open" : ""}`} onClick={() => toggle(t)}>{t.replace(/-/g, " ")}</button>
          ))}
        </div>
      )}
      <div className="notedots" role="radiogroup" aria-label="Note colour">
        {COLORS.map((c, i) => (
          <button key={c} type="button" role="radio" aria-checked={meta.color === i} aria-label={`Colour ${i + 1}`}
            className={`notedot${meta.color === i ? " on" : ""}`} style={{ ["--dot" as string]: c }} onClick={() => save({ ...meta, color: i })}>{meta.color === i ? "✓" : ""}</button>
        ))}
      </div>
    </div>
  );
}
