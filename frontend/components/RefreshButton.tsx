"use client";
import { useState } from "react";
import { hardRefresh } from "@/lib/refresh";

/** Always-visible refresh in the top bar. */
export default function RefreshButton() {
  const [busy, setBusy] = useState(false);
  return (
    <button className={busy ? "refreshbtn spin" : "refreshbtn"} title="Refresh" aria-label="Refresh the app"
      onClick={() => { setBusy(true); hardRefresh(); }}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7" />
      </svg>
    </button>
  );
}
