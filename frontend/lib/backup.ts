/** Backup and restore of the data that only lives in this browser (review schedule, solve times, goal, notes, layout…). */
const BLOCKED_EXACT = new Set(["lc-auth-token", "lc-auth-user", "lc-auth-email", "lc-client-id"]);
const BLOCKED_PREFIX = ["lc-cache:"];
const MAX_BYTES = 4_000_000;

export const isBackupKey = (k: string) =>
  k.startsWith("lc-") && !BLOCKED_EXACT.has(k) && !BLOCKED_PREFIX.some((p) => k.startsWith(p));

export interface Backup { app: "leetcode-practice"; version: 1; exportedAt: string; data: Record<string, string> }

export function buildBackup(storage: Pick<Storage, "length" | "key" | "getItem"> = localStorage): Backup {
  const data: Record<string, string> = {};
  for (let i = 0; i < storage.length; i++) {
    const k = storage.key(i);
    if (k && isBackupKey(k)) { const v = storage.getItem(k); if (v !== null) data[k] = v; }
  }
  return { app: "leetcode-practice", version: 1, exportedAt: new Date().toISOString(), data };
}

/** Validates a backup file's text; returns the entries that may be restored or throws a message fit for the user. */
export function parseBackup(text: string): Record<string, string> {
  if (text.length > MAX_BYTES) throw new Error("That file is too large to be a backup.");
  let j: unknown;
  try { j = JSON.parse(text); } catch { throw new Error("That file is not valid JSON."); }
  const b = j as Partial<Backup> | null;
  if (!b || b.app !== "leetcode-practice" || b.version !== 1 || typeof b.data !== "object" || b.data === null)
    throw new Error("That is not a LeetCode Practice backup.");
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(b.data)) if (isBackupKey(k) && typeof v === "string") out[k] = v;
  if (Object.keys(out).length === 0) throw new Error("The backup contains nothing to restore.");
  return out;
}
