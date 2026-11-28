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
      <h2 style={{ marginBottom: 4 }}>My submissions</h2>
      <div className="filters" style={{ margin: "8px 0" }}>
        <select value={verdict} aria-label="Filter by status" onChange={(e) => { setVerdict(e.target.value); setPage(0); }}>
          <option value="">All statuses</option>
          {VERDICTS.map((v) => <option key={v} value={v}>{label(v)}</option>)}
        </select>
        <span className="grow" />
        <Link href="/profile">← Profile</Link>
      </div>
      {error && <div className="banner err">{error}</div>}
      {!data && !error && <Skeleton />}
      {data && (
        <>
          <table className="subtable">
            <thead><tr><th>Time Submitted</th><th>Question</th><th>Status</th><th className="th-num">Runtime</th><th className="th-num">Memory</th><th>Language</th></tr></thead>
            <tbody>
              {data.items.map((s) => (
                <tr key={s.id}>
                  <td className="mute" title={new Date(s.createdAt).toLocaleString()}>{timeAgo(s.createdAt)}</td>
                  <td>{s.slug ? <Link href={`/problems/${s.slug}`}>{s.title}</Link> : s.title}</td>
                  <td className={s.verdict === "ACCEPTED" ? "ACCEPTED" : "REJECTED"}>
                    <b>{label(s.verdict)}</b>
                    {s.verdict !== "ACCEPTED" && s.total > 0 && <div className="mute" style={{ fontSize: 12, fontWeight: 400 }}>{s.passed}/{s.total} testcases passed</div>}
                  </td>
                  <td className="th-num">{s.runtimeMs != null ? `${s.runtimeMs} ms` : "N/A"}</td>
                  <td className="th-num">{s.memoryKb != null ? `${(s.memoryKb / 1024).toFixed(1)} MB` : "N/A"}</td>
                  <td><span className="langpill">{s.language}</span></td>
                </tr>
              ))}
              {data.items.length === 0 && <tr><td colSpan={6} className="mute">No submissions yet.</td></tr>}
            </tbody>
          </table>
          {data.totalPages > 1 && (
            <div className="bar" style={{ marginTop: 8 }}>
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
