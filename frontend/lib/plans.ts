import type { ProblemSummary } from "./api";

export interface Plan { id: string; title: string; blurb: string; match: (p: ProblemSummary) => boolean }
const has = (...tags: string[]) => (p: ProblemSummary) => p.tags.some((t) => tags.includes(t));

export const PLANS: Plan[] = [
  { id: "warmup", title: "Easy warm-up", blurb: "Every easy problem. Build speed and confidence.", match: (p) => p.difficulty === "EASY" },
  { id: "arrays", title: "Arrays & hashing", blurb: "Hash maps, prefix sums and sorting tricks.", match: has("array", "hash-table", "prefix-sum", "sorting") },
  { id: "pointers", title: "Two pointers, windows & binary search", blurb: "Linear-time scans and halving the search space.", match: has("two-pointers", "sliding-window", "binary-search") },
  { id: "stacks", title: "Stacks & heaps", blurb: "Monotonic stacks, priority queues and selection.", match: has("stack", "monotonic-stack", "heap", "quickselect") },
  { id: "dp", title: "Dynamic programming", blurb: "From climbing stairs to harder state machines.", match: has("dynamic-programming") },
  { id: "graphs", title: "Graphs & grids", blurb: "BFS, DFS, union-find and topological order.", match: has("graph", "bfs", "dfs", "union-find", "topological-sort", "matrix") },
  { id: "search", title: "Backtracking, greedy & intervals", blurb: "Explore, prune and choose locally-best moves.", match: has("backtracking", "greedy", "divide-and-conquer", "intervals") },
  { id: "bits", title: "Bits & math", blurb: "Bit tricks, number theory and sieves.", match: has("bit-manipulation", "math", "sieve") },
  { id: "medium", title: "Medium grind", blurb: "The core of most interviews.", match: (p) => p.difficulty === "MEDIUM" },
  { id: "hard", title: "Hard mode", blurb: "For when mediums feel easy.", match: (p) => p.difficulty === "HARD" },
];

const RANK = { EASY: 0, MEDIUM: 1, HARD: 2 } as const;
export const inPlan = (plan: Plan, all: ProblemSummary[]) =>
  all.filter(plan.match).sort((a, b) => RANK[a.difficulty] - RANK[b.difficulty] || a.id - b.id);
