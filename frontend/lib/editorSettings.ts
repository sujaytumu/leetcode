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
  if (editor === "dark") return "lc-black";
  if (editor === "light") return "vs";
  if (editor === "hc") return "hc-black";
  return site === "light" ? "vs" : "lc-black";
}

/** A true-black Monaco theme that matches the site's dark theme (neutral greys, no blue tint). */
export function registerThemes(monaco: { editor: { defineTheme: (name: string, data: unknown) => void } }): void {
  monaco.editor.defineTheme("lc-black", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#0b0b0c",
      "editor.foreground": "#ededef",
      "editorGutter.background": "#0b0b0c",
      "editor.lineHighlightBackground": "#151516",
      "editor.lineHighlightBorder": "#00000000",
      "editorLineNumber.foreground": "#74747a",
      "editorLineNumber.activeForeground": "#e4e4e7",
      "editor.selectionBackground": "#33333a",
      "editor.inactiveSelectionBackground": "#232327",
      "editorCursor.foreground": "#ffb21f",
      "editorIndentGuide.background1": "#232326",
      "editorWidget.background": "#111113",
      "editorSuggestWidget.background": "#111113",
      "scrollbarSlider.background": "#ffffff22",
    },
  });
}
