"use client";
import { useState } from "react";
import { clientId } from "@/lib/api";
import { authHeaders } from "@/lib/auth";

/** Downloads every accepted solution as a zip (one folder per problem + README index), ready for a GitHub repo. */
export default function ExportCard() {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  async function download() {
    setBusy(true); setMsg("");
    try {
      const res = await fetch("/api/export/solutions.zip", { headers: { "X-Client-Id": clientId(), ...authHeaders() } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const url = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = url; a.download = "leetcode-solutions.zip";
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
      setMsg("Downloaded.");
    } catch {
      setMsg("Couldn't download. The server may be starting up, try again in a moment.");
    } finally { setBusy(false); }
  }

  return (
    <section className="card">
      <h3 style={{ margin: "0 0 4px" }}>Export solutions</h3>
      <p className="mute" style={{ margin: "0 0 10px", fontSize: 13 }}>
        Your latest accepted solution per problem and language, one folder each with a README index. Drop it into a GitHub repo.
      </p>
      <div className="bar">
        <button className="primary" onClick={download} disabled={busy}>{busy ? "Preparing…" : "⬇ Download .zip"}</button>
        {msg && <span className="mute" style={{ fontSize: 13 }}>{msg}</span>}
      </div>
    </section>
  );
}
