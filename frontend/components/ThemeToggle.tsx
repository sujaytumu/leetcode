"use client";
import { useEffect, useState } from "react";

export type ThemeName = "dark" | "light";

/** Current theme as set on <html data-theme>; dark is the default. */
export function currentTheme(): ThemeName {
  return typeof document !== "undefined" && document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

/** Light/dark switch (sun/moon pill). The choice is remembered and announced to other components via a window event. */
export default function ThemeToggle() {
  const [theme, setTheme] = useState<ThemeName>("dark");
  useEffect(() => {
    setTheme(currentTheme());
    const sync = () => setTheme(currentTheme());
    window.addEventListener("lc-theme", sync);
    return () => window.removeEventListener("lc-theme", sync);
  }, []);

  function toggle() {
    const next: ThemeName = theme === "dark" ? "light" : "dark";
    const root = document.documentElement;
    // Fade colours for a moment so the switch feels smooth instead of snapping.
    root.classList.add("theme-anim");
    window.setTimeout(() => root.classList.remove("theme-anim"), 350);
    root.dataset.theme = next;
    try { localStorage.setItem("lc-theme", next); } catch { /* storage blocked */ }
    window.dispatchEvent(new Event("lc-theme"));
    setTheme(next);
  }

  const dark = theme === "dark";
  return (
    <button type="button" role="switch" aria-checked={dark} className={`theme-btn theme-switch ${dark ? "is-dark" : "is-light"}`}
      onClick={toggle} title={dark ? "Switch to light theme" : "Switch to dark theme"} aria-label="Dark theme">
      <span className="ts-track" aria-hidden="true">
        <svg className="ts-sun" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </svg>
        <svg className="ts-moon" viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
          <path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a.6.6 0 0 0-.8-.7A9.5 9.5 0 1 0 21.2 15a.6.6 0 0 0-.7-.8z" />
        </svg>
        <span className="ts-knob" />
      </span>
    </button>
  );
}
