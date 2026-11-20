import type { Plan } from "./api";

export type Level = "Beginner" | "Intermediate" | "Advanced";

/** Study plan level from its mix of difficulties, like the labels on LeetCode's Study Plan cards. */
export function planLevel(problems: { difficulty: string }[]): Level {
  if (problems.length === 0) return "Beginner";
  const share = (d: string) => problems.filter((p) => p.difficulty === d).length / problems.length;
  if (share("HARD") >= 0.25) return "Advanced";
  if (share("MEDIUM") + share("HARD") >= 0.5) return "Intermediate";
  return "Beginner";
}

const BANNERS = [
  ["#ffa116", "#ff6a3d"], ["#00b8a3", "#2d7ff9"], ["#a78bfa", "#ff6fa5"], ["#3ddc84", "#00b8a3"], ["#4da3ff", "#7c4dff"], ["#ff375f", "#ffa116"],
];

/** Stable gradient per plan, so each card keeps its colour between visits. */
export function bannerFor(id: string): [string, string] {
  let h = 0;
  for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return BANNERS[h % BANNERS.length] as [string, string];
}

export type PlanState = "start" | "continue" | "done";
export function planState(plan: Pick<Plan, "solved" | "total">): PlanState {
  return plan.solved >= plan.total && plan.total > 0 ? "done" : plan.solved === 0 ? "start" : "continue";
}
