"use client";
import { EditorSettings, EditorTheme } from "@/lib/editorSettings";

interface Props {
  settings: EditorSettings;
  onChange: (patch: Partial<EditorSettings>) => void;
  onReset: () => void;
  onClose: () => void;
}

const THEMES: { key: EditorTheme; label: string }[] = [
  { key: "auto", label: "Match site" }, { key: "dark", label: "Dark" },
  { key: "light", label: "Light" }, { key: "hc", label: "High contrast" },
];

/** LeetCode-style editor settings dialog. */
export default function EditorSettingsModal({ settings, onChange, onReset, onClose }: Props) {
  const toggle = (key: "wordWrap" | "minimap" | "lineNumbers", label: string) => (
    <label className="setting-row">
      <span>{label}</span>
      <input type="checkbox" checked={settings[key]} onChange={(e) => onChange({ [key]: e.target.checked })} />
    </label>
  );
  return (
    <div className="modal-back" onClick={onClose}>
      <div className="modal" role="dialog" aria-label="Editor settings" onClick={(e) => e.stopPropagation()}>
        <h3 style={{ marginTop: 0 }}>Editor settings</h3>
        <label className="setting-row">
          <span>Font size</span>
          <select value={settings.fontSize} onChange={(e) => onChange({ fontSize: Number(e.target.value) })}>
            {[12, 13, 14, 15, 16, 18, 20, 24].map((n) => <option key={n} value={n}>{n}px</option>)}
          </select>
        </label>
        <label className="setting-row">
          <span>Tab size</span>
          <select value={settings.tabSize} onChange={(e) => onChange({ tabSize: Number(e.target.value) })}>
            {[2, 4, 8].map((n) => <option key={n} value={n}>{n} spaces</option>)}
          </select>
        </label>
        <label className="setting-row">
          <span>Editor theme</span>
          <select value={settings.editorTheme} onChange={(e) => onChange({ editorTheme: e.target.value as EditorTheme })}>
            {THEMES.map((t) => <option key={t.key} value={t.key}>{t.label}</option>)}
          </select>
        </label>
        {toggle("wordWrap", "Word wrap")}
        {toggle("lineNumbers", "Line numbers")}
        {toggle("minimap", "Minimap")}
        <div className="bar" style={{ marginTop: 14 }}>
          <button onClick={onReset}>Reset to defaults</button>
          <span className="grow" />
          <button className="primary" onClick={onClose}>Done</button>
        </div>
      </div>
    </div>
  );
}
