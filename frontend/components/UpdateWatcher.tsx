"use client";
import { useEffect, useState } from "react";
import { hardRefresh, isWorkspace } from "@/lib/refresh";

const MINE = process.env.NEXT_PUBLIC_BUILD_ID ?? "dev";

/** Notices a newer deployment. Away from the code editor it refreshes by itself when you come back to the app; in the editor it asks first. */
export default function UpdateWatcher() {
  const [stale, setStale] = useState(false);

  useEffect(() => {
    if (MINE === "dev") return;
    let alive = true;
    const check = async () => {
      try {
        const r = await fetch("/version", { cache: "no-store" });
        const { id } = await r.json();
        if (!alive || !id || id === "dev" || id === MINE) return;
        if (document.visibilityState === "visible" && !isWorkspace()) hardRefresh(); else setStale(true);
      } catch { /* offline: try again later */ }
    };
    const onVisible = () => { if (document.visibilityState === "visible") check(); };
    document.addEventListener("visibilitychange", onVisible);
    const t = setInterval(check, 5 * 60 * 1000);
    check();
    return () => { alive = false; clearInterval(t); document.removeEventListener("visibilitychange", onVisible); };
  }, []);

  if (!stale) return null;
  return (
    <div className="install-toast" role="status">
      <span>A new version is ready.</span>
      <button className="primary" onClick={hardRefresh}>Refresh</button>
      <button onClick={() => setStale(false)}>Later</button>
    </div>
  );
}
