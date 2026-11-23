/* Offline support: the app shell, visited pages and the problem snapshot keep working without a connection.
   Backend API calls are cross-origin and are never touched here, so progress data is always live. */
const VERSION = "v1";
const STATIC = `lc-static-${VERSION}`;
const PAGES = `lc-pages-${VERSION}`;
const PRECACHE = ["/offline.html", "/icon-192.png", "/problems-snapshot.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(STATIC).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== STATIC && k !== PAGES).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  // Hashed build assets never change: serve from cache, fill on first use.
  if (url.pathname.startsWith("/_next/static/")) {
    event.respondWith(caches.open(STATIC).then(async (c) => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    }));
    return;
  }

  // Snapshot and icons: show the saved copy immediately, refresh it in the background.
  if (PRECACHE.includes(url.pathname)) {
    event.respondWith(caches.open(STATIC).then(async (c) => {
      const hit = await c.match(req);
      const refresh = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || refresh;
    }));
    return;
  }

  // Everything else (pages): network first, fall back to the last copy, then to the offline page.
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok && res.type === "basic") { const copy = res.clone(); caches.open(PAGES).then((c) => c.put(req, copy)); }
        return res;
      })
      .catch(async () => {
        const hit = await caches.match(req);
        if (hit) return hit;
        if (req.mode === "navigate") return (await caches.match("/offline.html")) || Response.error();
        return Response.error();
      }));
});
