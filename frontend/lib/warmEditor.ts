let warmed = false;

/**
 * Downloads the code editor in the background (when the browser is idle) so a problem page opens with it already cached.
 * Safe to call many times; it only ever starts one download, and a failed attempt can be retried.
 */
export function warmEditor(): void {
  if (warmed || typeof window === "undefined") return;
  warmed = true;
  const run = () => {
    import("@monaco-editor/react").then((m) => m.loader.init()).catch(() => { warmed = false; });
  };
  const idle = (window as unknown as { requestIdleCallback?: (cb: () => void, opts?: { timeout: number }) => number }).requestIdleCallback;
  if (idle) idle(run, { timeout: 4000 }); else window.setTimeout(run, 1500);
}
