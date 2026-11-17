"use client";
import { useEffect, useState } from "react";

export type ThemeName = "dark" | "light";

/** Current theme as set on <html data-theme>; dark is the default. */
export function currentTheme(): ThemeName {
  return typeof document !== "undefined" && document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

/** Light/dark switch. The choice is remembered and announced to other components via a window event. */
export default function ThemeToggle() {
  const [theme, setTheme] = useState<ThemeName>("dark");
  useEffect(() => setTheme(currentTheme()), []);

  function toggle() {
    const next: ThemeName = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("lc-theme", next); } catch { /* storage blocked */ }
    window.dispatchEvent(new Event("lc-theme"));
    setTheme(next);
  }

  return (
    <button className="theme-btn" onClick={toggle} title="Switch light / dark theme"
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}>
      {theme === "dark" ? "☀ Light" : "🌙 Dark"}
    </button>
  );
}
