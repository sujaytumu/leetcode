"use client";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";

type Phase = "show" | "fade" | "done";

/**
 * Full-screen loading page, separate from the app. It is part of the very first paint (server-rendered), so the app
 * never shows a half-loaded state underneath. It goes away as soon as the server answers; a sleeping free-tier server
 * can take a minute, so after a while it explains what is happening.
 */
export default function Splash() {
  const [phase, setPhase] = useState<Phase>("show");
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    let stop = false;
    const slowTimer = setTimeout(() => { if (!stop) setSlow(true); }, 6000);
    const started = Date.now();
    const up = async () => {
      const ctl = new AbortController();
      // A request to a sleeping server can hang; cut it and try again instead of waiting on a dead socket.
      const cut = setTimeout(() => ctl.abort(), 7000);
      try { const r = await fetch("/actuator/health", { cache: "no-store", signal: ctl.signal }); return r.ok; }
      catch { return false; }
      finally { clearTimeout(cut); }
    };
    (async () => {
      while (!stop) {
        if (await up()) break;
        if (Date.now() - started > 90000) break; // give up waiting; the pages show their own retry messages
        await new Promise((r) => setTimeout(r, 1000));
      }
      if (stop) return;
      clearTimeout(slowTimer);
      setPhase("fade");
    })();
    return () => { stop = true; clearTimeout(slowTimer); };
  }, []);

  useEffect(() => {
    if (phase !== "fade") return;
    const t = setTimeout(() => setPhase("done"), 220);
    return () => clearTimeout(t);
  }, [phase]);

  if (phase === "done") return null;
  return (
    <div className={`splash${phase === "fade" ? " out" : ""}`} role="status" aria-live="polite">
      <div className="splash-box">
        <div className="splash-logo"><Logo size={72} /></div>
        <div className="splash-name">LeetCode Practice</div>
        <div className="splash-load">Loading<span className="splash-dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span></div>
        <div className="splash-bar" aria-hidden="true"><i /></div>
        <p className="splash-note">{slow ? "Waking up the server. The first visit can take up to a minute." : " "}</p>
      </div>
    </div>
  );
}
