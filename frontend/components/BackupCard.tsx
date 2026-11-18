"use client";
import { useRef, useState } from "react";
import { buildBackup, parseBackup } from "@/lib/backup";

/** Download or restore the settings, notes, review schedule and solve times that are stored only in this browser. */
export default function BackupCard() {
  const file = useRef<HTMLInputElement>(null);
  const [msg, setMsg] = useState("");

  function download() {
    const blob = new Blob([JSON.stringify(buildBackup(), null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `leetcode-practice-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    setMsg("Backup downloaded. It has no password or login token in it.");
  }

  async function restore(f: File | undefined) {
    if (!f) return;
    try {
      const entries = parseBackup(await f.text());
      if (!window.confirm(`Restore ${Object.keys(entries).length} saved items? They replace the same items on this device.`)) return;
      for (const [k, v] of Object.entries(entries)) localStorage.setItem(k, v);
      setMsg("Restored. Reloading…");
      setTimeout(() => window.location.reload(), 600);
    } catch (e) { setMsg((e as Error).message); }
    if (file.current) file.current.value = "";
  }

  return (
    <section className="card">
      <h3 style={{ margin: "0 0 6px" }}>Device backup</h3>
      <p className="mute" style={{ margin: "0 0 10px", fontSize: 13 }}>
        Review schedule, solve times, daily goal, editor settings and layout live only in this browser. Save them to move to another device.
      </p>
      <div className="bar" style={{ flexWrap: "wrap" }}>
        <button onClick={download}>Download backup</button>
        <button onClick={() => file.current?.click()}>Restore from file…</button>
        <input ref={file} type="file" accept="application/json,.json" hidden onChange={(e) => restore(e.target.files?.[0])} />
      </div>
      {msg && <p className="mute" style={{ margin: "8px 0 0", fontSize: 13 }}>{msg}</p>}
    </section>
  );
}
