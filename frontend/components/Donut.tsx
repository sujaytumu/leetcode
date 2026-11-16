type By = Record<"EASY" | "MEDIUM" | "HARD", { total: number; solved: number }>;
const COLOR = { EASY: "#00b8a3", MEDIUM: "#ffb800", HARD: "#ff375f" } as const;

/** Progress ring in the style of LeetCode's profile: one arc per difficulty, filled in proportion to what is solved. */
export default function Donut({ by, solved, total, attempted }: { by: By; solved: number; total: number; attempted: number }) {
  const r = 46, C = 2 * Math.PI * r, gap = 3;
  let start = 0;
  const arcs = (["EASY", "MEDIUM", "HARD"] as const).map((d) => {
    const share = total ? by[d].total / total : 0;
    const len = Math.max(0, share * C - gap);
    const filled = by[d].total ? len * (by[d].solved / by[d].total) : 0;
    const a = { d, len, filled, start };
    start += share * C;
    return a;
  });
  return (
    <div className="donut" role="img" aria-label={`${solved} of ${total} solved`}>
      <svg width="112" height="112" viewBox="0 0 112 112">
        {arcs.map((a) => (
          <g key={a.d}>
            <circle cx="56" cy="56" r={r} fill="none" stroke={COLOR[a.d]} strokeOpacity=".22" strokeWidth="6" strokeLinecap="round"
              strokeDasharray={`${a.len} ${C}`} strokeDashoffset={-a.start} />
            {a.filled > 0 && (
              <circle cx="56" cy="56" r={r} fill="none" stroke={COLOR[a.d]} strokeWidth="6" strokeLinecap="round"
                strokeDasharray={`${a.filled} ${C}`} strokeDashoffset={-a.start} />
            )}
          </g>
        ))}
      </svg>
      <div className="mid">
        <b>{solved}<span style={{ fontSize: 13, fontWeight: 400 }}>/{total}</span></b>
        <span>Solved</span>
        {attempted > 0 && <span>{attempted} Attempting</span>}
      </div>
    </div>
  );
}
