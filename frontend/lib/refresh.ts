/** Throws away saved page copies and reloads, so the newest deployment and fresh data are shown. */
export async function hardRefresh() {
  try {
    if ("caches" in window) {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k.startsWith("lc-pages")).map((k) => caches.delete(k)));
    }
    if ("serviceWorker" in navigator) {
      const reg = await navigator.serviceWorker.getRegistration();
      await reg?.update();
    }
  } catch { /* refreshing still works without the cache clean-up */ }
  window.location.reload();
}

/** True while the person is likely typing code, where a silent reload would lose work. */
export function isWorkspace() {
  return window.location.pathname.startsWith("/problems/");
}
