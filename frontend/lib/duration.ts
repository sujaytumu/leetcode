export interface Parts { days: number; hours: number; minutes: number; seconds: number }

/** Splits a number of seconds (negative counts as zero) into the units shown on a contest countdown. */
export function splitDuration(totalSeconds: number): Parts {
  const s = Math.max(0, Math.floor(Number.isFinite(totalSeconds) ? totalSeconds : 0));
  return { days: Math.floor(s / 86400), hours: Math.floor((s % 86400) / 3600), minutes: Math.floor((s % 3600) / 60), seconds: s % 60 };
}
