"use client";
import { useEffect, useMemo, useRef } from "react";
import { api } from "./api";

interface Workspace {
  notes: { content: string; updatedAt: number };
  drafts: { language: string; code: string; updatedAt: number }[];
}

const DEBOUNCE_MS = 1200;
const noteKey = (slug: string) => `lc-notes:${slug}`;
const noteTs = (slug: string) => `lc-notes-ts:${slug}`;
const draftKey = (slug: string, lang: string) => `lc-draft2:${slug}:${lang}`;
const draftTs = (slug: string, lang: string) => `lc-draft2-ts:${slug}:${lang}`;
const num = (key: string) => Number(localStorage.getItem(key) ?? 0) || 0;

/**
 * Mirrors a problem's notes and per-language code drafts to the server so they follow the device sync code.
 * localStorage stays the instant cache; the server copy is applied when it is newer than what this device last synced.
 */
export function useCloudSync(
  slug: string,
  handlers: { onNotes: (text: string) => void; onDraft: (lang: string, code: string) => void },
) {
  const latest = useRef(handlers);
  latest.current = handlers;
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const putNotes = (text: string) =>
    api<{ updatedAt: number }>(`/api/problems/${slug}/workspace/notes`, { method: "PUT", body: JSON.stringify({ content: text }) })
      .then((r) => localStorage.setItem(noteTs(slug), String(r.updatedAt)));
  const putDraft = (lang: string, code: string) =>
    api<{ updatedAt: number }>(`/api/problems/${slug}/workspace/drafts/${lang}`, { method: "PUT", body: JSON.stringify({ code }) })
      .then((r) => localStorage.setItem(draftTs(slug, lang), String(r.updatedAt)));

  // Pull when a problem opens: adopt newer server copies, and upload anything that only exists on this device.
  useEffect(() => {
    let live = true;
    api<Workspace>(`/api/problems/${slug}/workspace`).then((ws) => {
      if (!live) return;
      const localNote = localStorage.getItem(noteKey(slug)) ?? "";
      if (ws.notes.updatedAt > num(noteTs(slug)) && ws.notes.content !== localNote) {
        localStorage.setItem(noteKey(slug), ws.notes.content);
        localStorage.setItem(noteTs(slug), String(ws.notes.updatedAt));
        latest.current.onNotes(ws.notes.content);
      } else if (ws.notes.updatedAt === 0 && localNote) {
        putNotes(localNote).catch(() => {});
      }
      const onServer = new Set<string>();
      for (const d of ws.drafts) {
        onServer.add(d.language);
        const local = localStorage.getItem(draftKey(slug, d.language));
        if (d.updatedAt > num(draftTs(slug, d.language)) && d.code !== local) {
          localStorage.setItem(draftKey(slug, d.language), d.code);
          localStorage.setItem(draftTs(slug, d.language), String(d.updatedAt));
          latest.current.onDraft(d.language, d.code);
        }
      }
      const prefix = `lc-draft2:${slug}:`;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(prefix)) {
          const lang = key.slice(prefix.length);
          const code = localStorage.getItem(key) ?? "";
          if (!onServer.has(lang) && code) putDraft(lang, code).catch(() => {});
        }
      }
    }).catch(() => { /* offline or waking up: local copy keeps working */ });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  return useMemo(() => {
    const debounced = (id: string, task: () => Promise<unknown>) => {
      clearTimeout(timers.current[id]);
      timers.current[id] = setTimeout(() => { task().catch(() => {}); }, DEBOUNCE_MS);
    };
    return {
      saveNotes: (text: string) => debounced("notes", () => putNotes(text)),
      saveDraft: (lang: string, code: string) => debounced(`draft:${lang}`, () => putDraft(lang, code)),
      clearDraft: (lang: string) => {
        clearTimeout(timers.current[`draft:${lang}`]);
        localStorage.removeItem(draftTs(slug, lang));
        api(`/api/problems/${slug}/workspace/drafts/${lang}`, { method: "DELETE" }).catch(() => {});
      },
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);
}
