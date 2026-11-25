"use client";
import { useCallback, useEffect, useRef } from "react";

let seq = 0;

/**
 * Makes the phone/browser Back button close an overlay (sheet, modal, drawer, workspace pane) instead of leaving the
 * page or the app: while `open`, one history entry is pushed; Back pops it and calls `close`. When the overlay is
 * closed some other way (tap, Done, Escape) the entry is popped again so history stays clean.
 *
 * Returns `dismiss(after?)`: closes the overlay and then runs `after` (typically `router.push`), removing the overlay's
 * history entry first so the navigation does not leave a stray "same page" entry behind.
 */
export function useBackClose(open: boolean, close: () => void): (after?: () => void) => void {
  const closeRef = useRef(close);
  closeRef.current = close;
  const idRef = useRef<string | null>(null);
  const afterRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!open) return;
    const id = `lc-ov-${++seq}`;
    try {
      // Keep Next's own history state (it uses it to restore pages) and add our marker.
      window.history.pushState({ ...(window.history.state ?? {}), lcOverlay: id }, "", window.location.href);
    } catch { return; }
    idRef.current = id;
    let popped = false;
    const onPop = () => {
      popped = true;
      idRef.current = null;
      closeRef.current();
      const after = afterRef.current;
      afterRef.current = null;
      after?.();
    };
    window.addEventListener("popstate", onPop, { once: true });
    return () => {
      window.removeEventListener("popstate", onPop);
      if (!popped && window.history.state?.lcOverlay === id) {
        idRef.current = null;
        try { window.history.back(); } catch { /* ignore */ }
      }
    };
  }, [open]);

  return useCallback((after?: () => void) => {
    const id = idRef.current;
    if (id && window.history.state?.lcOverlay === id) {
      afterRef.current = after ?? null;
      window.history.back(); // popstate runs close() then after()
    } else {
      closeRef.current();
      after?.();
    }
  }, []);
}
