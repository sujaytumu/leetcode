export interface Accent { key: string; label: string; dark: string; light: string }

/** Accent colours, each with a variant tuned for the dark and the light theme. */
export const ACCENTS: Accent[] = [
  { key: "amber", label: "Amber", dark: "#ffa116", light: "#e08a00" },
  { key: "blue", label: "Blue", dark: "#4da3ff", light: "#1c6fd1" },
  { key: "green", label: "Green", dark: "#3ddc84", light: "#1f9d55" },
  { key: "violet", label: "Violet", dark: "#a78bfa", light: "#7c4dff" },
  { key: "pink", label: "Pink", dark: "#ff6fa5", light: "#d6336c" },
  { key: "teal", label: "Teal", dark: "#2dd4bf", light: "#0f9488" },
];

export const ACCENT_KEY = "lc-accent";

export function accentByKey(key: string | null | undefined): Accent | null {
  return ACCENTS.find((a) => a.key === key) ?? null;
}

/** Applies (or, with null, clears) the accent on <html>. The CSS picks the dark or light variant by theme. */
export function applyAccent(a: Accent | null, root: HTMLElement = document.documentElement): void {
  if (!a || a.key === "amber") {
    root.style.removeProperty("--accent-d"); root.style.removeProperty("--accent-l");
  } else {
    root.style.setProperty("--accent-d", a.dark); root.style.setProperty("--accent-l", a.light);
  }
}

export function saveAccent(a: Accent): void {
  try { localStorage.setItem(ACCENT_KEY, a.key); } catch { /* storage blocked */ }
  applyAccent(a);
}

/** Inline script body for <head>, so the saved accent is in place before first paint. */
export const ACCENT_BOOT_SCRIPT =
  `try{var a=${JSON.stringify(ACCENTS.filter((x) => x.key !== "amber"))}.find(function(x){return x.key===localStorage.getItem(${JSON.stringify(ACCENT_KEY)})});` +
  `if(a){var s=document.documentElement.style;s.setProperty('--accent-d',a.dark);s.setProperty('--accent-l',a.light)}}catch(e){}`;
