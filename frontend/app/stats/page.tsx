"use client";
import BackLink from "@/components/BackLink";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, tagLabel, type Page, type Profile } from "@/lib/api";
import { AreaChart, Columns, Donut, Legend, Radar, type Slice } from "@/components/charts";
import Skeleton from "@/components/Skeleton";
import { allTimes, fmtSecs } from "@/lib/times";

interface Item {
  id: number; slug: string; title: string; verdict: string; language: string;
  passed: number; total: number; runtimeMs: number | null; memoryKb: number | null; createdAt: string;
}
const label = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** Every submission of the caller, following pagination (the server caps a page at 100); stops at 2000 to stay quick. */
async function loadAll(): Promise<Item[]> {
  const out: Item[] = [];
  for (let page = 0; page < 20; page++) {
    const d = await api<Page<Item>>(`/api/submissions?page=${page}&size=100`);
    out.push(...d.items);
    if (page + 1 >= d.totalPages) break;
  }
  return out;
}

function Bars({ rows, color }: { rows: { name: string; value: number; note?: string }[]; color?: string }) {
  const max = Math.max(1, ...rows.map((r) => r.value));
  return (
    <div className="hbars">
      {rows.map((r) => (
        <div key={r.name} className="hbar">
          <span className="hb-name">{r.name}</span>
          <span className="hb-track"><span style={{ width: `${(r.value / max) * 100}%`, background: color ?? "var(--accent)" }} /></span>
          <span className="hb-val">{r.value}{r.note ? ` ${r.note}` : ""}</span>
        </div>
      ))}
    </div>
  );
}

export default function StatsPage() {
  usePageTitle("My stats");
  const [items, setItems] = useState<Item[] | null>(null);
  const [error, setError] = useState("");
  const [times, setTimes] = useState<{ slug: string; best: number; runs: number }[]>([]);
  useEffect(() => { setTimes(Object.entries(allTimes()).map(([slug, r]) => ({ slug, best: r.best, runs: r.runs })).sort((a, b) => a.best - b.best)); }, []);
  const [profile, setProfile] = useState<Profile | null>(null);
  useEffect(() => { api<Profile>("/api/profile").then(setProfile).catch(() => setProfile(null)); }, []);
  useEffect(() => { loadAll().then(setItems).catch((e: Error) => setError(e.message)); }, []);

  const s = useMemo(() => {
    if (!items) return null;
    const total = items.length, ac = items.filter((i) => i.verdict === "ACCEPTED").length;
    const verdicts = new Map<string, number>(), langs = new Map<string, { n: number; ac: number }>();
    const weekday = new Array<number>(7).fill(0), hour = new Array<number>(24).fill(0);
    const byProblem = new Map<string, Item[]>();
    for (const i of items) {
      verdicts.set(i.verdict, (verdicts.get(i.verdict) ?? 0) + 1);
      const l = langs.get(i.language) ?? { n: 0, ac: 0 };
      l.n++; if (i.verdict === "ACCEPTED") l.ac++;
      langs.set(i.language, l);
      const d = new Date(i.createdAt);
      weekday[d.getDay()]++; hour[d.getHours()]++;
      (byProblem.get(i.slug || i.title) ?? byProblem.set(i.slug || i.title, []).get(i.slug || i.title)!).push(i);
    }
    // Per problem: attempts (oldest first) until the first accepted one.
    let solved = 0, firstTry = 0, attemptsSum = 0;
    const struggles: { title: string; slug: string; tries: number; solved: boolean }[] = [];
    for (const list of byProblem.values()) {
      const asc = [...list].sort((a, b) => a.id - b.id);
      const k = asc.findIndex((x) => x.verdict === "ACCEPTED");
      if (k >= 0) { solved++; attemptsSum += k + 1; if (k === 0) firstTry++; }
      struggles.push({ title: asc[0].title, slug: asc[0].slug, tries: k >= 0 ? k + 1 : asc.length, solved: k >= 0 });
    }
    struggles.sort((a, b) => b.tries - a.tries);
    const mostActiveHour = hour.indexOf(Math.max(...hour));
    const titles = new Map<string, string>(items.map((i) => [i.slug, i.title]));
    // Day-by-day series (local dates): cumulative submissions/accepted since the first one, and the last 30 days.
    const key = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const perDay = new Map<string, { n: number; ac: number }>();
    for (const i of items) {
      const k = key(new Date(i.createdAt));
      const v = perDay.get(k) ?? { n: 0, ac: 0 };
      v.n++; if (i.verdict === "ACCEPTED") v.ac++;
      perDay.set(k, v);
    }
    const first = new Date(Math.min(...items.map((i) => new Date(i.createdAt).getTime())));
    first.setHours(0, 0, 0, 0);
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const trendLabels: string[] = [], cumAll: number[] = [], cumAc: number[] = [];
    let a = 0, b = 0;
    for (const d = new Date(first); d <= today && trendLabels.length < 400; d.setDate(d.getDate() + 1)) {
      const v = perDay.get(key(d));
      a += v?.n ?? 0; b += v?.ac ?? 0;
      trendLabels.push(d.toLocaleDateString(undefined, { day: "numeric", month: "short" }));
      cumAll.push(a); cumAc.push(b);
    }
    const dayLabels: string[] = [], dayCounts: number[] = [];
    for (let k = 29; k >= 0; k--) {
      const d = new Date(today); d.setDate(d.getDate() - k);
      dayLabels.push(d.toLocaleDateString(undefined, { day: "numeric", month: "short" }));
      dayCounts.push(perDay.get(key(d))?.n ?? 0);
    }
    return { trendLabels, cumAll, cumAc, dayLabels, dayCounts, total, ac, verdicts, langs, weekday, hour, solved, firstTry, attemptsSum, struggles: struggles.slice(0, 5),
      problems: byProblem.size, mostActiveHour, titles };
  }, [items]);

  if (error) return <div className="banner err">{error}</div>;
  if (!s) return <Skeleton lines={8} />;
  if (s.total === 0) return <p className="mute">No submissions yet. Submit a solution and your stats show up here.</p>;

  const VERDICT_COLOR: Record<string, string> = {
    ACCEPTED: "var(--easy)", WRONG_ANSWER: "var(--hard)", TIME_LIMIT_EXCEEDED: "var(--med)",
    RUNTIME_ERROR: "#8b7be0", COMPILE_ERROR: "#2fb5a3", MEMORY_LIMIT_EXCEEDED: "#d46bb0",
  };
  const verdictSlices: Slice[] = [...s.verdicts].sort((a, b) => (a[0] === "ACCEPTED" ? -1 : b[0] === "ACCEPTED" ? 1 : b[1] - a[1]))
    .map(([k, v]) => ({ label: label(k), value: v, color: VERDICT_COLOR[k] ?? "var(--mute)" }));
  const bd = profile?.progress.byDifficulty ?? {};
  const diffSlices: Slice[] = [["EASY", "var(--easy)"], ["MEDIUM", "var(--med)"], ["HARD", "var(--hard)"]]
    .map(([k, color]) => ({ label: label(k), value: bd[k]?.solved ?? 0, color }));
  const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 100)}%` : "–");
  return (
    <>
      <div className="bar" style={{ marginBottom: 10 }}>
        <h2 style={{ margin: 0 }}>My stats</h2><span className="grow" />
        <Link href="/submissions" className="softlink">All submissions</Link><BackLink fallback="/profile" />
      </div>
      <div className="cards">
        <div className="card"><span className="mute">Submissions</span><b>{s.total}</b></div>
        <div className="card"><span className="mute">Acceptance rate</span><b>{pct(s.ac, s.total)}</b></div>
        <div className="card"><span className="mute">Problems solved</span><b>{s.solved}<span className="mute" style={{ fontSize: 14 }}> / {s.problems} tried</span></b></div>
        <div className="card"><span className="mute">First-try solves</span><b>{pct(s.firstTry, s.solved)}</b></div>
        <div className="card"><span className="mute">Avg attempts to solve</span><b>{s.solved ? (s.attemptsSum / s.solved).toFixed(1) : "–"}</b></div>
      </div>
      <div className="vizgrid">
        <section className="card">
          <h3 style={{ margin: "0 0 8px" }}>Verdicts</h3>
          <div className="vizrow">
            <Donut slices={verdictSlices} centre={pct(s.ac, s.total)} sub="accepted" />
            <Legend slices={verdictSlices} />
          </div>
        </section>
        {profile && (
          <section className="card">
            <h3 style={{ margin: "0 0 8px" }}>Solved by difficulty</h3>
            <div className="vizrow">
              <Donut slices={diffSlices} centre={String(profile.progress.solved)} sub={`of ${profile.progress.total}`} />
              <Legend slices={diffSlices} />
            </div>
          </section>
        )}
        <section className="card wide">
          <h3 style={{ margin: "0 0 4px" }}>Progress over time</h3>
          <p className="mute" style={{ fontSize: 12, margin: "0 0 6px" }}>Running total of submissions and accepted solutions, day by day.</p>
          <AreaChart labels={s.trendLabels} series={[{ name: "Submissions", color: "var(--mute)", values: s.cumAll }, { name: "Accepted", color: "var(--easy)", values: s.cumAc }]} />
          <Legend row slices={[{ label: "Submissions", value: s.total, color: "var(--mute)" }, { label: "Accepted", value: s.ac, color: "var(--easy)" }]} />
        </section>
        <section className="card wide">
          <h3 style={{ margin: "0 0 4px" }}>Last 30 days</h3>
          <p className="mute" style={{ fontSize: 12, margin: "0 0 6px" }}>{s.dayCounts.reduce((n, v) => n + v, 0)} submissions, {s.dayCounts.filter((v) => v > 0).length} active days.</p>
          <Columns labels={s.dayLabels} values={s.dayCounts} />
        </section>
        {profile && profile.skills.length >= 3 && (
          <section className="card wide">
            <h3 style={{ margin: "0 0 4px" }}>Topic strengths</h3>
            <p className="mute" style={{ fontSize: 12, margin: "0 0 6px" }}>Problems solved in your {Math.min(8, profile.skills.length)} strongest topics.</p>
            <div className="vizrow center"><Radar axes={[...profile.skills].sort((a, b) => b.solved - a.solved).slice(0, 8).map((k) => ({ label: tagLabel(k.tag), value: k.solved }))} /></div>
          </section>
        )}
      </div>
      <div className="statgrid">
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>Verdicts</h3>
          <Bars rows={[...s.verdicts].sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ name: label(k), value: v, note: `(${pct(v, s.total)})` }))} /></section>
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>Languages</h3>
          <Bars rows={[...s.langs].sort((a, b) => b[1].n - a[1].n).map(([k, v]) => ({ name: k, value: v.n, note: `(${pct(v.ac, v.n)} AC)` }))} /></section>
        <section className="card"><h3 style={{ margin: "0 0 8px" }}>By weekday</h3>
          <Bars rows={s.weekday.map((v, i) => ({ name: DAYS[i], value: v }))} color="var(--easy)" /></section>
        <section className="card"><h3 style={{ margin: "0 0 4px" }}>By hour of day</h3>
          <p className="mute" style={{ fontSize: 12, margin: "0 0 8px" }}>You submit most around {String(s.mostActiveHour).padStart(2, "0")}:00.</p>
          <div className="hourbars" aria-label="Submissions by hour">
            {s.hour.map((v, h) => <span key={h} title={`${String(h).padStart(2, "0")}:00 · ${v}`} style={{ height: `${(v / Math.max(1, ...s.hour)) * 100}%` }} />)}
          </div></section>
        {times.length > 0 && (
          <section className="card" style={{ gridColumn: "1 / -1" }}>
            <h3 style={{ margin: "0 0 4px" }}>Timed solves</h3>
            <p className="mute" style={{ fontSize: 12, margin: "0 0 8px" }}>
              {times.length} problem{times.length === 1 ? "" : "s"} timed · average best {fmtSecs(Math.round(times.reduce((n, t) => n + t.best, 0) / times.length))}
            </p>
            {times.slice(0, 5).map((t) => (
              <div key={t.slug} className="recentrow" style={{ cursor: "default" }}>
                <Link href={`/problems/${t.slug}`}>{s.titles.get(t.slug) ?? t.slug}</Link><span className="grow" />
                <span className="mute" style={{ fontSize: 13 }}>best {fmtSecs(t.best)} · {t.runs} timed solve{t.runs === 1 ? "" : "s"}</span>
              </div>
            ))}
          </section>
        )}
        <section className="card" style={{ gridColumn: "1 / -1" }}><h3 style={{ margin: "0 0 8px" }}>Problems that took the most attempts</h3>
          {s.struggles.map((p) => (
            <div key={p.slug || p.title} className="recentrow" style={{ cursor: "default" }}>
              {p.slug ? <Link href={`/problems/${p.slug}`}>{p.title}</Link> : <span>{p.title}</span>}
              <span className="grow" />
              <span className="mute" style={{ fontSize: 13 }}>{p.tries} attempt{p.tries === 1 ? "" : "s"} · {p.solved ? "solved" : "unsolved"}</span>
            </div>
          ))}</section>
      </div>
    </>
  );
}
