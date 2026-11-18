"use client";
import { useState } from "react";

type Level = "Advanced" | "Intermediate" | "Fundamental";
const LEVELS: { level: Level; color: string }[] = [
  { level: "Advanced", color: "var(--hard)" },
  { level: "Intermediate", color: "var(--med)" },
  { level: "Fundamental", color: "var(--easy)" },
];

const ADVANCED = new Set(["Dynamic Programming", "Backtracking", "Divide and Conquer", "Trie", "Segment Tree", "Union Find",
  "Binary Indexed Tree", "Monotonic Stack", "Topological Sort", "Memoization"]);
const FUNDAMENTAL = new Set(["Array", "String", "Sorting", "Counting Sort"]);
/** Short tag names used by the seed data, mapped to the names LeetCode shows. */
const ALIAS: Record<string, string> = {
  dp: "Dynamic Programming", dfs: "Depth-First Search", bfs: "Breadth-First Search", bst: "Binary Search Tree",
};

function pretty(tag: string): string {
  if (ALIAS[tag]) return ALIAS[tag];
  return tag.split("-").map((w) => (w === "and" ? w : w[0].toUpperCase() + w.slice(1))).join(" ")
    .replace("Depth First", "Depth-First").replace("Breadth First", "Breadth-First");
}
const levelOf = (name: string): Level => (ADVANCED.has(name) ? "Advanced" : FUNDAMENTAL.has(name) ? "Fundamental" : "Intermediate");

/** Tag counts grouped like LeetCode's Skills section. Aliases of one topic (dp / dynamic-programming) show as one chip. */
export default function SkillsCard({ skills }: { skills: { tag: string; solved: number }[] }) {
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const merged = new Map<string, number>();
  for (const s of skills) {
    const name = pretty(s.tag);
    merged.set(name, Math.max(merged.get(name) ?? 0, s.solved));
  }
  const groups = LEVELS.map(({ level, color }) => ({
    level, color,
    items: [...merged].filter(([name]) => levelOf(name) === level).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])),
  })).filter((g) => g.items.length > 0);

  if (groups.length === 0) return <p className="mute">Topics you solve appear here.</p>;
  return (
    <div>
      {groups.map((g) => {
        const all = open[g.level], shown = all ? g.items : g.items.slice(0, 3);
        return (
          <div key={g.level} className="skillgroup">
            <div className="skilllevel"><span className="dot" style={{ background: g.color }} />{g.level}</div>
            <div className="skillchips">
              {shown.map(([name, n]) => <span key={name} className="skillchip">{name}<span className="mute"> x{n}</span></span>)}
            </div>
            {g.items.length > 3 && (
              <button type="button" className="showmore" onClick={() => setOpen({ ...open, [g.level]: !all })}>{all ? "Show less" : "Show more"}</button>
            )}
          </div>
        );
      })}
    </div>
  );
}
