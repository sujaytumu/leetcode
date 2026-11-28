"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import { type Page } from "@/lib/api";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";
import { timeAgo } from "@/lib/timeago";

interface Item {
  id: number; slug: string; title: string; verdict: string; language: string;
  passed: number; total: number; runtimeMs: number | null; memoryKb: number | null; createdAt: string;
}

const VERDICTS = ["ACCEPTED", "WRONG_ANSWER", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED", "COMPILE_ERROR"];
const ICON: Record<string, string> = { ACCEPTED: "✓", WRONG_ANSWER: "✕", RUNTIME_ERROR: "!", TIME_LIMIT_EXCEEDED: "⏱", MEMORY_LIMIT_EXCEEDED: "⏱", COMPILE_ERROR: "{ }" };
const label = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

export default function SubmissionsPage() {
  usePageTitle("My submissions");
  const [verdict, setVerdict] = useState("");
  const [page, setPage] = useState(0);
  const [data, setData] = useState<Page<Item> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null); setError("");
    const q = new URLSearchParams({ page: String(page), size: "20" });
    if (verdict) q.set("verdict", verdict);
    let current = true; // a slow answer for an earlier filter or page must not replace this one
    swr<Page<Item>>(`/api/submissions?${q}`, (d) => { if (current) setData(d); }, () => {})
      .catch((e: Error) => { if (current) setError(e.message); });
    return () => { current = false; };
  }, [verdict, page]);

  return (
    <>
      <span className="narrowmark" hidden />
      <div className="sb-head">
        <div>
          <h2>My submissions</h2>
          {data && <p className="mute">{data.totalElements} {verdict ? label(verdict).toLowerCase() : "in total"}</p>}
        </div>
        <Link className="sb-back" href="/profile">← Profile</Link>
      </div>
      <div className="sb-chips" role="tablist" aria-label="Filter by status">
        <button type="button" role="tab" aria-selected={verdict === ""} className={verdict === "" ? "on" : ""} onClick={() => { setVerdict(""); setPage(0); }}>All</button>
        {VERDICTS.map((v) => (
          <button key={v} type="button" role="tab" aria-selected={verdict === v} className={`${v} ${verdict === v ? "on" : ""}`} onClick={() => { setVerdict(v); setPage(0); }}>
            <i aria-hidden="true">{ICON[v]}</i>{label(v)}
          </button>
        ))}
      </div>
      {error && <div className="banner err">{error}</div>}
      {!data && !error && <Skeleton />}
      {data && (
        <>
          <table className="subtable subcute">
            <thead><tr><th>Time Submitted</th><th>Question</th><th>Status</th><th className="th-num">Runtime</th><th className="th-num">Memory</th><th>Language</th></tr></thead>
            <tbody>
              {data.items.map((s) => (
                <tr key={s.id}>
                  <td className="mute" title={new Date(s.createdAt).toLocaleString()}>{timeAgo(s.createdAt)}</td>
                  <td>{s.slug ? <Link href={`/problems/${s.slug}`}>{s.title}</Link> : s.title}</td>
                  <td>
                    <span className={`vbadge ${s.verdict}`}><i aria-hidden="true">{ICON[s.verdict] ?? "!"}</i>{label(s.verdict)}</span>
                    {s.verdict !== "ACCEPTED" && s.total > 0 && (
                      <div className="vpass" title={`${s.passed} of ${s.total} testcases passed`}>
                        <span className="vpass-bar"><i style={{ width: `${(s.passed / s.total) * 100}%` }} /></span>
                        <span className="mute">{s.passed}/{s.total} passed</span>
                      </div>
                    )}
                  </td>
                  <td className="th-num"><span className="metric">{s.runtimeMs != null ? `${s.runtimeMs} ms` : "N/A"}</span></td>
                  <td className="th-num"><span className="metric">{s.memoryKb != null ? `${(s.memoryKb / 1024).toFixed(1)} MB` : "N/A"}</span></td>
                  <td><span className="langpill">{s.language}</span></td>
                </tr>
              ))}
              {data.items.length === 0 && <tr className="sb-empty"><td colSpan={6}>{verdict ? "Nothing with this status yet." : "No submissions yet. Solve a problem and it shows up here."}</td></tr>}
            </tbody>
          </table>
          {data.totalPages > 1 && (
            <div className="sb-pager">
              <button disabled={page === 0} onClick={() => setPage(page - 1)}>← Prev</button>
              <span className="mute">Page {page + 1} of {data.totalPages}</span>
              <button disabled={page + 1 >= data.totalPages} onClick={() => setPage(page + 1)}>Next →</button>
            </div>
          )}
        </>
      )}
    </>
  );
}
