"use client";
import { useEffect, useState, useSyncExternalStore } from "react";
import { loading } from "@/lib/loading";

/** A thin progress bar plus one word, shown only while the site is actually waiting on the server. */
export default function LoadingIndicator() {
  const busy = useSyncExternalStore(loading.subscribe, loading.active, () => false);
  const [show, setShow] = useState(false);
  useEffect(() => {
    if (!busy) { setShow(false); return; }
    const t = setTimeout(() => setShow(true), 250); // skip the flash for instant responses
    return () => clearTimeout(t);
  }, [busy]);
  if (!show) return null;
  return (
    <>
      <div className="topbar" aria-hidden="true" />
      <span className="loading-word" role="status">Loading…</span>
    </>
  );
}
