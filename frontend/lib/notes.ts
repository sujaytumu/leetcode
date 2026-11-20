export interface NoteEntry { slug: string; text: string; updatedAt: number }

const PREFIX = "lc-notes:";

/** Every non-empty note saved on this device, newest first. */
export function listNotes(storage: Pick<Storage, "length" | "key" | "getItem">): NoteEntry[] {
  const out: NoteEntry[] = [];
  for (let i = 0; i < storage.length; i++) {
    const k = storage.key(i);
    if (!k || !k.startsWith(PREFIX)) continue;
    const text = storage.getItem(k) ?? "";
    if (!text.trim()) continue;
    const slug = k.slice(PREFIX.length);
    const ts = Number(storage.getItem(`lc-notes-ts:${slug}`));
    out.push({ slug, text, updatedAt: Number.isFinite(ts) && ts > 0 ? ts : 0 });
  }
  return out.sort((a, b) => b.updatedAt - a.updatedAt || a.slug.localeCompare(b.slug));
}

/** Case-insensitive match on the note text or the problem title/slug. */
export function filterNotes(list: NoteEntry[], query: string, titles: Map<string, string>): NoteEntry[] {
  const q = query.trim().toLowerCase();
  if (!q) return list;
  return list.filter((n) => n.text.toLowerCase().includes(q) || n.slug.includes(q) || (titles.get(n.slug) ?? "").toLowerCase().includes(q));
}

export function toMarkdown(list: NoteEntry[], titles: Map<string, string>): string {
  return list.map((n) => `## ${titles.get(n.slug) ?? n.slug}\n\n${n.text.trim()}\n`).join("\n");
}
