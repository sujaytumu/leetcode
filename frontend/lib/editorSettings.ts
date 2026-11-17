"use client";
import { useCallback, useEffect, useState } from "react";

export type EditorTheme = "auto" | "dark" | "light" | "hc";

export interface EditorSettings {
  fontSize: number;
  tabSize: number;
  wordWrap: boolean;
  minimap: boolean;
  lineNumbers: boolean;
  editorTheme: EditorTheme;
}

export const DEFAULT_EDITOR_SETTINGS: EditorSettings = {
  fontSize: 14, tabSize: 4, wordWrap: false, minimap: false, lineNumbers: true, editorTheme: "auto",
};

const KEY = "lc-editor-settings";

function read(): EditorSettings {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) ?? "null");
    if (saved && typeof saved === "object") return { ...DEFAULT_EDITOR_SETTINGS, ...saved };
    const legacyFont = Number(localStorage.getItem("lc-font")); // from before this panel existed
    if (legacyFont) return { ...DEFAULT_EDITOR_SETTINGS, fontSize: legacyFont };
  } catch { /* storage blocked or corrupt: fall back to defaults */ }
  return DEFAULT_EDITOR_SETTINGS;
}

/** Editor preferences, remembered in this browser. */
export function useEditorSettings(): [EditorSettings, (patch: Partial<EditorSettings>) => void, () => void] {
  const [settings, setSettings] = useState<EditorSettings>(DEFAULT_EDITOR_SETTINGS);
  useEffect(() => setSettings(read()), []);
  const update = useCallback((patch: Partial<EditorSettings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...patch };
      try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* ignore */ }
      return next;
    });
  }, []);
  const reset = useCallback(() => {
    setSettings(DEFAULT_EDITOR_SETTINGS);
    try { localStorage.removeItem(KEY); } catch { /* ignore */ }
  }, []);
  return [settings, update, reset];
}

/** Monaco theme id for the chosen editor theme; "auto" follows the site theme. */
export function monacoTheme(editor: EditorTheme, site: "dark" | "light"): string {
  if (editor === "dark") return "vs-dark";
  if (editor === "light") return "vs";
  if (editor === "hc") return "hc-black";
  return site === "light" ? "vs" : "vs-dark";
}
