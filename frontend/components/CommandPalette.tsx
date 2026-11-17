"use client";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api, Page, ProblemSummary } from "@/lib/api";

const PAGES = [
  { label: "Problems", hint: "Browse all problems", href: "/" },
  { label: "Topics", hint: "Problems grouped by topic", href: "/topics" },
  { label: "For you", hint: "What to solve next and what to revisit", href: "/for-you" },
  { label: "Daily challenge calendar", hint: "Every day's problem this month", href: "/daily" },
  { label: "Study plans", hint: "Curated learning paths", href: "/plans" },
  { label: "Profile", hint: "Your progress and activity", href: "/profile" },
];

type Item = { key: string; label: string; hint: string; href: string; difficulty?: string };

/** Header button that opens the palette (works with touch too). */
export function PaletteButton() {
  const [mac, setMac] = useState(false);
  useEffect(() => setMac(/Mac|iPhone|iPad/.test(navigator.platform)), []);
  return (
    <button className="palette-btn" onClick={() => window.dispatchEvent(new Event("lc-palette"))} aria-label="Search problems">
      <span aria-hidden="true">🔍</span><span className="hide-sm"> Search</span>
      <kbd className="hide-sm">{mac ? "⌘K" : "Ctrl K"}</kbd>
    </button>
  );
}

/** Ctrl/⌘+K or "/" opens a quick-jump search over problems (served by the backend) and pages. */
export default function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [found, setFound] = useState<ProblemSummary[]>([]);
  const [sel, setSel] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const seq = useRef(0);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      const typing = !!t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); setOpen((o) => !o); return; }
      if (e.key === "/" && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); setOpen(true); }
      if (e.key === "Escape") setOpen(false);
    };
    const onOpen = () => setOpen(true);
    window.addEventListener("keydown", onKey);
    window.addEventListener("lc-palette", onOpen);
    return () => { window.removeEventListener("keydown", onKey); window.removeEventListener("lc-palette", onOpen); };
  }, []);

  useEffect(() => { if (open) { setQ(""); setFound([]); setSel(0); setTimeout(() => input.current?.focus(), 0); } }, [open]);

  useEffect(() => {
    if (!open) return;
    const term = q.trim();
    if (!term) { setFound([]); return; }
    const mine = ++seq.current;
    const t = setTimeout(() => {
      api<Page<ProblemSummary>>(`/api/problems?q=${encodeURIComponent(term)}&page=0`)
        .then((p) => { if (mine === seq.current) { setFound(p.items.slice(0, 8)); setSel(0); } })
        .catch(() => { if (mine === seq.current) setFound([]); });
    }, 180);
    return () => clearTimeout(t);
  }, [q, open]);

  const term = q.trim().toLowerCase();
  const items: Item[] = [
    ...found.map((p) => ({
      key: `p-${p.id}`, label: `${p.number ?? p.id}. ${p.title}`, hint: p.tags.slice(0, 3).join(", "),
      href: `/problems/${p.slug}`, difficulty: p.difficulty,
    })),
    ...PAGES.filter((p) => !term || p.label.toLowerCase().includes(term)).map((p) => ({ key: `g-${p.href}`, ...p })),
  ];

  const go = (it: Item | undefined) => { if (!it) return; setOpen(false); router.push(it.href); };
  const onInputKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setSel((s) => Math.min(items.length - 1, s + 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setSel((s) => Math.max(0, s - 1)); }
    else if (e.key === "Enter") { e.preventDefault(); go(items[sel]); }
  };

  if (!open) return null;
  return (
    <div className="modal-back palette-back" onClick={() => setOpen(false)}>
      <div className="modal palette" role="dialog" aria-label="Search" onClick={(e) => e.stopPropagation()}>
        <input ref={input} className="palette-input" placeholder="Search problems or jump to a page…" value={q}
          onChange={(e) => setQ(e.target.value)} onKeyDown={onInputKey} />
        <ul className="palette-list">
          {items.map((it, i) => (
            <li key={it.key} className={i === sel ? "on" : ""} onMouseEnter={() => setSel(i)} onClick={() => go(it)}>
              <span>{it.label}</span>
              <span className="mute palette-hint">
                {it.difficulty && <span className={it.difficulty}>{it.difficulty[0] + it.difficulty.slice(1).toLowerCase()} · </span>}{it.hint}
              </span>
            </li>
          ))}
          {term && found.length === 0 && items.length === 0 && <li className="mute">No matches</li>}
        </ul>
        <div className="mute palette-foot"><kbd>↑</kbd> <kbd>↓</kbd> navigate · <kbd>↵</kbd> open · <kbd>Esc</kbd> close</div>
      </div>
    </div>
  );
}
