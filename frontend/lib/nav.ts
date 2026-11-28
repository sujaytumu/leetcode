"use client";
/** Position of the current screen in this session's history (0 = the first screen the app opened). */
export const position = () => (typeof window === "undefined" ? 0 : (window.history.state?.__lcIdx as number | undefined) ?? 0);

declare global { interface Window { __lcIdxPatched?: boolean } }

/** Stamps every history entry with its position so Back knows when there is nothing earlier left in the app. */
export function trackPositions() {
  if (typeof window === "undefined" || window.__lcIdxPatched) return;
  window.__lcIdxPatched = true;
  const push = window.history.pushState.bind(window.history);
  const replace = window.history.replaceState.bind(window.history);
  window.history.pushState = (s, t, u) => push({ ...(s ?? {}), __lcIdx: position() + 1 }, t, u);
  window.history.replaceState = (s, t, u) => replace({ ...(s ?? {}), __lcIdx: position() }, t, u);
}

/** True when an earlier screen of this app is in the history, so Back can return to it. */
export const canGoBack = () => position() > 0;
