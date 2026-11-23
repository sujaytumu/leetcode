"use client";
import { useEffect, useState } from "react";

const COLORS = ["#ffc01e", "#ff7a18", "#2cd3b4", "#3b9dff", "#ff5577", "#a855f7"];

/** A short burst of confetti when a submission is Accepted. Purely decorative (aria-hidden) and skipped for reduced motion. */
export default function Confetti({ burst }: { burst: number }) {
  const [show, setShow] = useState(false);
  useEffect(() => {
    if (!burst) return;
    if (typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    setShow(true);
    const t = setTimeout(() => setShow(false), 2400);
    return () => clearTimeout(t);
  }, [burst]);
  if (!show) return null;
  return (
    <div className="confetti" aria-hidden="true">
      {Array.from({ length: 44 }, (_, i) => {
        const angle = (i / 44) * Math.PI * 2 + (i % 3) * 0.2;
        const dist = 160 + ((i * 53) % 220);
        return (
          <i key={i} style={{
            ["--dx" as string]: `${Math.cos(angle) * dist}px`, ["--dy" as string]: `${Math.sin(angle) * dist - 120}px`,
            ["--rot" as string]: `${(i * 97) % 720}deg`, background: COLORS[i % COLORS.length], animationDelay: `${(i % 6) * 18}ms`,
            width: 6 + (i % 3) * 2, height: 9 + (i % 4) * 2,
          }} />
        );
      })}
    </div>
  );
}
