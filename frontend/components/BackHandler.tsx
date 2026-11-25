"use client";
import { useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";

declare global { interface Window { __lcBack?: () => boolean; __lcIdxPatched?: boolean } }

/** Position of the current screen in this session's history (0 = the first screen the app opened). */
const position = () => (window.history.state?.__lcIdx as number | undefined) ?? 0;

/** Stamps every history entry with its position so Back knows when there is nothing earlier left in the app. */
function trackPositions() {
  if (window.__lcIdxPatched) return;
  window.__lcIdxPatched = true;
  const push = window.history.pushState.bind(window.history);
  const replace = window.history.replaceState.bind(window.history);
  window.history.pushState = (s, t, u) => push({ ...(s ?? {}), __lcIdx: position() + 1 }, t, u);
  window.history.replaceState = (s, t, u) => replace({ ...(s ?? {}), __lcIdx: position() }, t, u);
}

/**
 * Android app only (the native shell asks `window.__lcBack()` on the phone's Back button): go one screen back; from the
 * first screen go to the Problems tab; from there let the app go to the background. Overlays that use useBackClose
 * keep their own history entry, so Back closes them first.
 */
export default function BackHandler() {
  const path = usePathname() ?? "/";
  const router = useRouter();
  const pathRef = useRef(path);
  pathRef.current = path;

  useEffect(() => {
    if (!navigator.userAgent.includes("LeetcodeApp")) return;
    trackPositions();
    window.__lcBack = () => {
      if (position() > 0) { window.history.back(); return true; }
      if (pathRef.current !== "/problemset") { router.replace("/problemset"); return true; }
      return false;
    };
    return () => { delete window.__lcBack; };
  }, [router]);

  return null;
}
