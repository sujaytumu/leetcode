"use client";
import { useEffect, useState } from "react";
import { ACCENT_KEY, ACCENTS, accentByKey, saveAccent } from "@/lib/appearance";

/** Pick the colour used for buttons, links and highlights. Saved on this device. */
export default function AppearanceCard() {
  const [key, setKey] = useState("amber");
  useEffect(() => { setKey(accentByKey(localStorage.getItem(ACCENT_KEY))?.key ?? "amber"); }, []);
  return (
    <section className="card">
      <h3 style={{ margin: "0 0 8px" }}>Accent colour</h3>
      <div className="swatches" role="radiogroup" aria-label="Accent colour">
        {ACCENTS.map((a) => (
          <button key={a.key} type="button" role="radio" aria-checked={key === a.key} aria-label={a.label} title={a.label}
            className={`swatch${key === a.key ? " on" : ""}`} style={{ background: a.dark }}
            onClick={() => { setKey(a.key); saveAccent(a); }} />
        ))}
      </div>
    </section>
  );
}
