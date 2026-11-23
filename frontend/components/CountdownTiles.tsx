import { splitDuration } from "@/lib/duration";

/** LeetCode-style countdown: boxed days, hours, minutes and seconds under a label. */
export default function CountdownTiles({ label, seconds }: { label: string; seconds: number }) {
  const p = splitDuration(seconds);
  const tiles: [number, string][] = [[p.days, "Days"], [p.hours, "Hours"], [p.minutes, "Mins"], [p.seconds, "Secs"]];
  return (
    <div className="cdtiles" role="timer" aria-label={`${label} ${p.days} days ${p.hours} hours ${p.minutes} minutes ${p.seconds} seconds`}>
      <div className="mute cdlabel">{label}</div>
      <div className="cdrow">
        {tiles.map(([n, u]) => (
          <div key={u} className="cdtile"><b>{String(n).padStart(2, "0")}</b><span>{u}</span></div>
        ))}
      </div>
    </div>
  );
}
