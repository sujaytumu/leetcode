"use client";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";
import "@/app/wake.css";

type Phase = "check" | "show" | "fade" | "done";

/**
 * Full-screen loading page, separate from the app. It appears only if the server hasn't answered after a moment
 * (a sleeping free-tier server can take a minute), sits in the middle of the screen, and fades away into the page
 * once the server is up, so the app itself never has to show a half-loaded state.
 */
export default function Splash() {
  const [phase, setPhase] = useState<Phase>("check");
  const [slow, setSlow] = useState(false);
  const [waking, setWaking] = useState(false); // server still asleep, but the app is already usable from its cache

  useEffect(() => {
    let stop = false;
    // The app paints from its cached catalogue straight away, so the full-screen splash is only a brief intro (first
    // visit only) and never holds the app hostage while a sleeping free-tier server wakes; a small pill shows instead.
    let seen = false;
    try { seen = localStorage.getItem("lc-seen") === "1"; localStorage.setItem("lc-seen", "1"); } catch { /* storage blocked */ }
    const showTimer = setTimeout(() => { if (!stop && !seen) setPhase((p) => (p === "check" ? "show" : p)); }, 450);
    const capTimer = setTimeout(() => { if (!stop) { setPhase((p) => (p === "show" ? "fade" : "done")); setWaking(true); } }, seen ? 800 : 2200);
    const slowTimer = setTimeout(() => { if (!stop) setSlow(true); }, 9000);
    const started = Date.now();
    const up = async () => {
      try { const r = await fetch("/actuator/health", { cache: "no-store" }); return r.ok; } catch { return false; }
    };
    (async () => {
      while (!stop) {
        if (await up()) break;
        if (Date.now() - started > 90000) break; // give up waiting; let the pages show their own retry messages
        await new Promise((r) => setTimeout(r, 2000));
      }
      if (stop) return;
      clearTimeout(showTimer); clearTimeout(capTimer);
      setWaking(false);
      setPhase((p) => (p === "show" ? "fade" : "done"));
    })();
    return () => { stop = true; clearTimeout(showTimer); clearTimeout(capTimer); clearTimeout(slowTimer); };
  }, []);

  useEffect(() => {
    if (phase !== "fade") return;
    const t = setTimeout(() => setPhase("done"), 350);
    return () => clearTimeout(t);
  }, [phase]);

  if (phase === "check" || phase === "done") {
    return waking ? (
      <div className="wakepill" role="status" aria-live="polite"><i aria-hidden="true" />{slow ? "Waking the server… cached content is shown meanwhile" : "Connecting to the server…"}</div>
    ) : null;
  }
  return (
    <div className={`splash${phase === "fade" ? " out" : ""}`} role="status" aria-live="polite">
      <div className="splash-box">
        <div className="splash-logo"><Logo size={72} /></div>
        <div className="splash-name">LeetCode Practice</div>
        <div className="splash-load">Loading<span className="splash-dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span></div>
        <div className="splash-bar" aria-hidden="true"><i /></div>
        <p className="splash-note">{slow ? "Waking up the server. The first visit can take up to a minute." : " "}</p>
      </div>
    </div>
  );
}
