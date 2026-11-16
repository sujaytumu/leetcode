import type { Status } from "@/lib/api";

/** Solved = green check in a circle, attempted = amber half circle, todo = nothing (as on LeetCode's problem list). */
export function StatusIcon({ status }: { status: Status }) {
  if (status === "SOLVED") {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-label="Solved" role="img" style={{ verticalAlign: "middle" }}>
        <circle cx="12" cy="12" r="9.5" stroke="#00b8a3" strokeWidth="2" /><path d="m7.5 12.5 3 3 6-6.5" stroke="#00b8a3" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (status === "ATTEMPTED") {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-label="Attempted" role="img" style={{ verticalAlign: "middle" }}>
        <circle cx="12" cy="12" r="9.5" stroke="#ffb800" strokeWidth="2" /><path d="M12 2.5a9.5 9.5 0 0 1 0 19Z" fill="#ffb800" />
      </svg>
    );
  }
  return null;
}

export const ChevronLeft = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
);
export const ChevronRight = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6" /></svg>
);
export const ListIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" /></svg>
);
export const PlayIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12-7.5a1 1 0 0 0 0-1.72l-12-7.5A1 1 0 0 0 7 4.5Z" /></svg>
);
export const CodeIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00b8a3" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="m16 18 6-6-6-6M8 6l-6 6 6 6" /></svg>
);
