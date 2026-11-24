"use client";
import { useEffect, useRef, useState } from "react";
import { hardRefresh, isWorkspace } from "@/lib/refresh";

const TRIGGER = 80;

/** True when something under the finger can scroll up first, so the page shouldn't start a refresh. */
function scrollsFirst(el: Element | null): boolean {
  for (let n: Element | null = el; n && n !== document.body; n = n.parentElement) {
    if (n.matches("input, textarea, select, .monaco-editor, [contenteditable]")) return true;
    const oy = getComputedStyle(n).overflowY;
    if ((oy === "auto" || oy === "scroll") && n.scrollHeight > n.clientHeight && n.scrollTop > 0) return true;
  }
  return false;
}

/** Pull down from the top of any page to refresh it (not on the code workspace, where a swipe could be a selection). */
export default function PullToRefresh() {
  const [pull, setPull] = useState(0);
  const [busy, setBusy] = useState(false);
  const start = useRef<number | null>(null);
  const pullRef = useRef(0);

  useEffect(() => {
    const set = (v: number) => { pullRef.current = v; setPull(v); };
    const onStart = (e: TouchEvent) => {
      start.current = null;
      if (e.touches.length !== 1 || window.scrollY > 0 || isWorkspace() || scrollsFirst(e.target as Element)) return;
      start.current = e.touches[0].clientY;
    };
    const onMove = (e: TouchEvent) => {
      if (start.current === null) return;
      const dy = e.touches[0].clientY - start.current;
      if (dy <= 0 || window.scrollY > 0) { if (pullRef.current) set(0); return; }
      set(Math.min(dy * 0.5, 120));
    };
    const onEnd = () => {
      if (start.current === null) return;
      start.current = null;
      if (pullRef.current >= TRIGGER / 2 + 10) { setBusy(true); set(60); hardRefresh(); } else set(0);
    };
    document.addEventListener("touchstart", onStart, { passive: true });
    document.addEventListener("touchmove", onMove, { passive: true });
    document.addEventListener("touchend", onEnd);
    document.addEventListener("touchcancel", onEnd);
    return () => {
      document.removeEventListener("touchstart", onStart);
      document.removeEventListener("touchmove", onMove);
      document.removeEventListener("touchend", onEnd);
      document.removeEventListener("touchcancel", onEnd);
    };
  }, []);

  if (!pull && !busy) return null;
  const ready = pull >= TRIGGER / 2 + 10;
  return (
    <div className="ptr" style={{ transform: `translate(-50%, ${pull - 44}px)` }} role="status" aria-live="polite">
      <svg className={busy ? "spin" : ""} style={busy ? undefined : { transform: `rotate(${pull * 4}deg)` }} width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7" />
      </svg>
      <span>{busy ? "Refreshing…" : ready ? "Release to refresh" : "Pull to refresh"}</span>
    </div>
  );
}
