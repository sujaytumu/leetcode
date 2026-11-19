"use client";
/** Small dependency-free SVG charts. Colours come from the theme variables so dark and light both work. */

export interface Slice { label: string; value: number; color: string }

/** Donut with a centre label. Zero-value slices are skipped; hover shows the slice's share. */
export function Donut({ slices, centre, sub, size = 168 }: { slices: Slice[]; centre: string; sub?: string; size?: number }) {
  const total = slices.reduce((n, s) => n + s.value, 0);
  const r = 62, c = 2 * Math.PI * r;
  let acc = 0;
  return (
    <svg viewBox="0 0 160 160" width={size} height={size} role="img" aria-label={`${centre} ${sub ?? ""}`}>
      <circle cx="80" cy="80" r={r} fill="none" stroke="var(--cell)" strokeWidth="16" />
      {total > 0 && slices.filter((s) => s.value > 0).map((s) => {
        const len = (s.value / total) * c;
        const el = (
          <circle key={s.label} cx="80" cy="80" r={r} fill="none" stroke={s.color} strokeWidth="16"
            strokeDasharray={`${Math.max(0, len - 1.5)} ${c}`} strokeDashoffset={-acc} transform="rotate(-90 80 80)">
            <title>{`${s.label}: ${s.value} (${Math.round((s.value / total) * 100)}%)`}</title>
          </circle>
        );
        acc += len;
        return el;
      })}
      <text x="80" y={sub ? 80 : 86} textAnchor="middle" fontSize="26" fontWeight="700" fill="var(--text)">{centre}</text>
      {sub && <text x="80" y="100" textAnchor="middle" fontSize="11" fill="var(--mute)">{sub}</text>}
    </svg>
  );
}

export function Legend({ slices, row }: { slices: Slice[]; row?: boolean }) {
  return (
    <ul className={`chartlegend${row ? " row" : ""}`}>
      {slices.map((s) => (
        <li key={s.label}><span style={{ background: s.color }} />{s.label}<b>{s.value}</b></li>
      ))}
    </ul>
  );
}

export interface Series { name: string; color: string; values: number[] }

/** Line + soft area chart over shared x labels, with a hover column per point. */
export function AreaChart({ labels, series, height = 200 }: { labels: string[]; series: Series[]; height?: number }) {
  const W = 1000, H = height, L = 34, R = 8, T = 10, B = 22;
  const n = labels.length;
  if (n < 2) return <p className="mute" style={{ fontSize: 13 }}>Not enough days of activity to draw a trend yet.</p>;
  const max = Math.max(1, ...series.flatMap((s) => s.values));
  const nice = Math.max(1, Math.ceil(max / 4) * 4);
  const x = (i: number) => L + (i / (n - 1)) * (W - L - R);
  const y = (v: number) => T + (1 - v / nice) * (H - T - B);
  const ticks = [0, 1, 2, 3, 4].map((k) => (nice / 4) * k);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="areachart" role="img"
      aria-label={series.map((s) => `${s.name} reaches ${s.values[n - 1]}`).join(", ")}>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--line)" strokeDasharray={t === 0 ? undefined : "3 4"} />
          <text x={L - 6} y={y(t) + 3} textAnchor="end" fontSize="10" fill="var(--mute)">{Math.round(t)}</text>
        </g>
      ))}
      {series.map((s) => {
        const pts = s.values.map((v, i) => `${x(i)},${y(v)}`).join(" ");
        return (
          <g key={s.name}>
            <polygon points={`${x(0)},${y(0)} ${pts} ${x(n - 1)},${y(0)}`} fill={s.color} opacity="0.12" />
            <polyline points={pts} fill="none" stroke={s.color} strokeWidth="2" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
          </g>
        );
      })}
      {labels.map((lab, i) => (
        <rect key={i} x={x(i) - (W - L - R) / (n - 1) / 2} y={T} width={(W - L - R) / (n - 1)} height={H - T - B} fill="transparent">
          <title>{`${lab}\n${series.map((s) => `${s.name}: ${s.values[i]}`).join("\n")}`}</title>
        </rect>
      ))}
      <text x={L} y={H - 6} fontSize="10" fill="var(--mute)">{labels[0]}</text>
      <text x={W - R} y={H - 6} fontSize="10" fill="var(--mute)" textAnchor="end">{labels[n - 1]}</text>
    </svg>
  );
}

/** Spider chart for 3+ axes; values are drawn relative to the largest. */
export function Radar({ axes, size = 520 }: { axes: { label: string; value: number }[]; size?: number }) {
  const n = axes.length;
  if (n < 3) return <p className="mute" style={{ fontSize: 13 }}>Solve problems in at least three topics to see your radar.</p>;
  const cx = 200, cy = 140, R = 100;
  const max = Math.max(1, ...axes.map((a) => a.value));
  const pt = (i: number, f: number): [number, number] => {
    const a = (-Math.PI / 2) + (i / n) * 2 * Math.PI;
    return [cx + Math.cos(a) * R * f, cy + Math.sin(a) * R * f];
  };
  const ring = (f: number) => axes.map((_, i) => pt(i, f).join(",")).join(" ");
  const shape = axes.map((a, i) => pt(i, a.value / max).join(",")).join(" ");
  return (
    <svg viewBox="-50 0 500 280" style={{ width: "100%", maxWidth: size, height: "auto" }} role="img" aria-label="Topic strengths">
      {[0.25, 0.5, 0.75, 1].map((f) => <polygon key={f} points={ring(f)} fill="none" stroke="var(--line)" />)}
      {axes.map((_, i) => { const [px, py] = pt(i, 1); return <line key={i} x1={cx} y1={cy} x2={px} y2={py} stroke="var(--line)" />; })}
      <polygon points={shape} fill="var(--accent)" opacity="0.22" stroke="var(--accent)" strokeWidth="2" strokeLinejoin="round" />
      {axes.map((a, i) => {
        const [px, py] = pt(i, a.value / max);
        const [lx, ly] = pt(i, 1.2);
        return (
          <g key={a.label}>
            <circle cx={px} cy={py} r="3" fill="var(--accent)"><title>{`${a.label}: ${a.value}`}</title></circle>
            <text x={lx} y={ly + 3} fontSize="11" fill="var(--mute)" textAnchor={lx < cx - 4 ? "end" : lx > cx + 4 ? "start" : "middle"}>{a.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

/** Day-by-day columns (e.g. the last 30 days) with the busiest day highlighted. */
export function Columns({ labels, values, color = "var(--accent)", height = 120 }: { labels: string[]; values: number[]; color?: string; height?: number }) {
  const n = values.length, max = Math.max(1, ...values);
  const W = 1000, H = height, B = 16, bw = W / n;
  const top = values.indexOf(Math.max(...values));
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="areachart" role="img" aria-label="Activity per day">
      <line x1="0" x2={W} y1={H - B} y2={H - B} stroke="var(--line)" />
      {values.map((v, i) => {
        const h = v === 0 ? 2 : Math.max(4, (v / max) * (H - B - 6));
        return (
          <rect key={i} x={i * bw + 2} y={H - B - h} width={Math.max(1, bw - 4)} height={h} rx="2"
            fill={v === 0 ? "var(--cell)" : color} opacity={i === top && v > 0 ? 1 : 0.75}>
            <title>{`${labels[i]}: ${v}`}</title>
          </rect>
        );
      })}
      <text x="2" y={H - 3} fontSize="10" fill="var(--mute)">{labels[0]}</text>
      <text x={W - 2} y={H - 3} fontSize="10" fill="var(--mute)" textAnchor="end">{labels[n - 1]}</text>
    </svg>
  );
}
