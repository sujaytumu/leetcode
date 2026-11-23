"use client";
import { useEffect, useRef, useState } from "react";
import { Profile } from "@/lib/api";
import { authToken, authUser } from "@/lib/auth";
import { cardData, drawCard } from "@/lib/shareCard";

/** A shareable PNG of your progress: download it or hand it to the phone's share sheet. */
export default function ShareCard({ p, name }: { p: Profile; name: string }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [msg, setMsg] = useState("");
  // The name goes on the picture only for a signed-in account, matching the rest of the app.
  const shown = typeof window !== "undefined" && authToken() ? name || authUser() || "" : "";

  useEffect(() => { if (canvas.current) drawCard(canvas.current, cardData(p, shown)); }, [p, shown]);

  const toBlob = () => new Promise<Blob | null>((res) => canvas.current ? canvas.current.toBlob(res, "image/png") : res(null));

  async function download() {
    const blob = await toBlob();
    if (!blob) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "my-leetcode-progress.png"; a.click();
    URL.revokeObjectURL(a.href);
    setMsg("Saved.");
  }

  async function share() {
    const blob = await toBlob();
    if (!blob) return;
    const file = new File([blob], "my-leetcode-progress.png", { type: "image/png" });
    try {
      if (navigator.canShare?.({ files: [file] })) { await navigator.share({ files: [file], title: "My coding progress" }); return; }
    } catch { return; /* cancelled */ }
    await download();
  }

  return (
    <section className="card">
      <h3 style={{ margin: "0 0 8px" }}>Share your progress</h3>
      <canvas ref={canvas} aria-label="Progress card preview" style={{ width: "100%", height: "auto", borderRadius: 10, display: "block" }} />
      <div className="bar" style={{ marginTop: 10 }}>
        <button className="primary" onClick={share}>Share</button>
        <button onClick={download}>Download PNG</button>
        {msg && <span className="mute" style={{ fontSize: 13 }}>{msg}</span>}
      </div>
    </section>
  );
}
