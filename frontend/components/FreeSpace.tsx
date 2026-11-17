"use client";
import { useEffect, useState } from "react";

/** Loading / error state shown in the free space where the content will appear (never inside filters or tables). */
export default function FreeSpace({ loading, error, onRetry, label = "Loading…", compact = false }: {
  loading: boolean; error?: string; onRetry?: () => void; label?: string; compact?: boolean;
}) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!loading || error) { setSlow(false); return; }
    const t = setTimeout(() => setSlow(true), 6000);
    return () => clearTimeout(t);
  }, [loading, error]);
  const cls = `free-space${compact ? " compact" : ""}`;
  if (error) {
    return (
      <div className={cls} role="alert">
        <div className="free-msg err">{error}</div>
        {onRetry && <button onClick={onRetry}>Retry</button>}
      </div>
    );
  }
  if (!loading) return null;
  return (
    <div className={cls} role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <div className="mute">{label}</div>
      {slow && <div className="mute free-slow">Waking up the server — the free plan can take 1–3 minutes. Retrying automatically…</div>}
    </div>
  );
}
