import type { ProblemSummary } from "./api";

export interface ListSummary { id: number; name: string; count: number; contains: boolean }
export interface ListDetail { id: number; name: string; problems: ProblemSummary[] }
export const MAX_LISTS = 20;
