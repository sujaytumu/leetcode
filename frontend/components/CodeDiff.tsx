"use client";
import { useMemo } from "react";
import { diffLines } from "@/lib/diff";

/** Side-by-side-free unified diff: red lines were removed, green lines were added. */
export default function CodeDiff({ before, after }: { before: string; after: string }) {
  const lines = useMemo(() => diffLines(before, after), [before, after]);
  const added = lines.filter((l) => l.kind === "add").length, removed = lines.filter((l) => l.kind === "del").length;
  return (
    <div>
      <div className="mute" style={{ fontSize: 12, marginBottom: 4 }}>
        <span className="diff-add-n">+{added}</span> <span className="diff-del-n">−{removed}</span>
      </div>
      <pre className="subcode codediff">
        {lines.map((l, i) => (
          <div key={i} className={`dl ${l.kind}`}>
            <span className="dm">{l.kind === "add" ? "+" : l.kind === "del" ? "−" : " "}</span>{l.text || " "}
          </div>
        ))}
      </pre>
    </div>
  );
}
