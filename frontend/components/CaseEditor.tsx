"use client";
import { useEffect, useRef, useState } from "react";
import { buildInput, formatInputParts } from "@/lib/example";

/**
 * LeetCode's Testcase editor: one labelled box per argument (`nums =`, `target =`).
 * Edits are turned back into the judge's stdin text; a box that does not parse stays red until it does.
 */
export default function CaseEditor({ python, value, onChange }: { python: string; value: string; onChange: (stdin: string) => void }) {
  const parts = formatInputParts(python, value);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const emitted = useRef<string>(value);

  useEffect(() => {
    if (value !== emitted.current) { setDrafts({}); emitted.current = value; }
  }, [value]);

  if (!parts) {
    return <textarea className="consoletext" spellCheck={false} value={value} onChange={(e) => onChange(e.target.value)} aria-label="Test case input" />;
  }
  const shown = parts.map((p) => ({ name: p.name, value: drafts[p.name] ?? p.value }));

  function edit(name: string, text: string) {
    const next = shown.map((p) => (p.name === name ? { name, value: text } : p));
    setDrafts((d) => ({ ...d, [name]: text }));
    const stdin = buildInput(python, next);
    if (stdin !== null) { emitted.current = stdin; onChange(stdin); }
  }

  return (
    <div className="caseargs">
      {shown.map((p) => {
        const bad = buildInput(python, shown) === null;
        return (
          <label key={p.name} className="caseArg">
            <span className="argname">{p.name} =</span>
            <input className={`argbox${bad && drafts[p.name] !== undefined ? " bad" : ""}`} spellCheck={false} value={p.value}
              onChange={(e) => edit(p.name, e.target.value)} aria-label={p.name} />
          </label>
        );
      })}
    </div>
  );
}
