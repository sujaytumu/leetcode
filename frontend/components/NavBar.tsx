"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type State = "checking" | "waking" | "online" | "offline";
const LABEL: Record<State, string> = {
  checking: "Connecting", waking: "Waking server", online: "Server online", offline: "Server offline",
};

/** Polls the backend so a sleeping free-tier server is visible (and recovers on its own) instead of looking broken. */
function useServerState(): State {
  const [state, setState] = useState<State>("checking");
  useEffect(() => {
    let alive = true;
    let timer: ReturnType<typeof setTimeout>;
    let misses = 0;
    const tick = async () => {
      try {
        await api("/api/execution/status", {}, 15000);
        misses = 0;
        if (alive) setState("online");
        timer = setTimeout(tick, 120000);
      } catch {
        misses++;
        if (alive) setState(misses > 30 ? "offline" : "waking");
        timer = setTimeout(tick, misses > 30 ? 120000 : 5000);
      }
    };
    tick();
    return () => { alive = false; clearTimeout(timer); };
  }, []);
  return state;
}

export default function NavBar() {
  const path = usePathname();
  const server = useServerState();
  return (
    <header className="nav">
      <Link href="/" className="brand"><b>&lt;/&gt;</b> LeetCode <span className="long">Practice</span></Link>
      <nav>
        <Link href="/" className={path === "/" || path.startsWith("/problems") ? "on" : ""}>Problems</Link>
        <Link href="/plans" className={path.startsWith("/plans") ? "on" : ""}>Study Plan</Link>
      </nav>
      <span className={`srv ${server}`} title="Run and Submit need the backend, which sleeps on free hosting when idle">
        <i /> <span className="t">{LABEL[server]}</span>
      </span>
    </header>
  );
}
