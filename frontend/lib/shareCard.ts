import type { Profile } from "./api";

export interface CardData {
  name: string; solved: number; total: number; streak: number; maxStreak: number; activeDays: number;
  easy: [number, number]; medium: [number, number]; hard: [number, number]; topSkills: string[];
}

/** Pure mapping from the profile response to what the card shows, so it can be tested without a canvas. */
export function cardData(p: Profile, name: string): CardData {
  const d = (k: string): [number, number] => [p.progress.byDifficulty[k]?.solved ?? 0, p.progress.byDifficulty[k]?.total ?? 0];
  return {
    name: name || "Anonymous coder",
    solved: p.progress.solved, total: p.progress.total,
    streak: p.currentStreak, maxStreak: p.maxStreak, activeDays: p.activeDays,
    easy: d("EASY"), medium: d("MEDIUM"), hard: d("HARD"),
    topSkills: [...p.skills].sort((a, b) => b.solved - a.solved).slice(0, 3).map((s) => s.tag),
  };
}

const W = 1200, H = 630;

/** Draws a 1200x630 progress card (the size social previews use) and returns the canvas. */
export function drawCard(canvas: HTMLCanvasElement, c: CardData): void {
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d");
  if (!g) return;
  const bg = g.createLinearGradient(0, 0, W, H);
  bg.addColorStop(0, "#111827"); bg.addColorStop(1, "#1f2937");
  g.fillStyle = bg; g.fillRect(0, 0, W, H);
  g.fillStyle = "#f59e0b"; g.fillRect(0, 0, 14, H);

  const font = (px: number, w = 600) => { g.font = `${w} ${px}px -apple-system, Segoe UI, Roboto, sans-serif`; };
  g.textBaseline = "alphabetic";
  g.fillStyle = "#9ca3af"; font(30, 500); g.fillText("LeetCode Practice", 70, 90);
  g.fillStyle = "#f9fafb"; font(60, 700); g.fillText(c.name.slice(0, 28), 70, 170);

  g.fillStyle = "#f59e0b"; font(150, 800); g.fillText(String(c.solved), 70, 340);
  const numW = g.measureText(String(c.solved)).width;
  g.fillStyle = "#9ca3af"; font(44, 500); g.fillText(`/ ${c.total} solved`, 70 + numW + 20, 340);

  const bars: [string, [number, number], string][] = [["Easy", c.easy, "#22c55e"], ["Medium", c.medium, "#f59e0b"], ["Hard", c.hard, "#ef4444"]];
  bars.forEach(([label, [s, t], color], i) => {
    const y = 400 + i * 62;
    g.fillStyle = "#d1d5db"; font(28, 500); g.fillText(label, 70, y + 26);
    g.fillStyle = "#374151"; g.fillRect(230, y, 520, 22);
    g.fillStyle = color; g.fillRect(230, y, t ? Math.max(6, (520 * s) / t) : 0, 22);
    g.fillStyle = "#f9fafb"; font(28, 600); g.fillText(`${s}/${t}`, 770, y + 24);
  });

  g.fillStyle = "#f9fafb"; font(56, 700); g.fillText(`${c.streak}`, 900, 300);
  g.fillStyle = "#9ca3af"; font(26, 500); g.fillText("day streak", 900, 338);
  g.fillStyle = "#f9fafb"; font(56, 700); g.fillText(`${c.maxStreak}`, 900, 430);
  g.fillStyle = "#9ca3af"; font(26, 500); g.fillText("best streak", 900, 468);
  g.fillStyle = "#f9fafb"; font(56, 700); g.fillText(`${c.activeDays}`, 900, 560);
  g.fillStyle = "#9ca3af"; font(26, 500); g.fillText("active days", 900, 598);
  if (c.topSkills.length) { g.fillStyle = "#9ca3af"; font(24, 500); g.fillText(`Strongest: ${c.topSkills.join(", ")}`, 70, 600); }
}
