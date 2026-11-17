"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Page } from "@/lib/api";
import Skeleton from "@/components/Skeleton";

interface Item {
  id: number; slug: string; title: string; verdict: string; language: string;
  passed: number; total: number; runtimeMs: number | null; memoryKb: number | null; createdAt: string;
}

const VERDICTS = ["ACCEPTED", "WRONG_ANSWER", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED", "COMPILE_ERROR"];
const label = (v: string) => v.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

export default function SubmissionsPage() {
  const [verdict, setVerdict] = useState("");
  const [page, setPage] = useState(0);
  const [data, setData] = useState<Page<Item> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null); setError("");
    const q = new URLSearchParams({ page: String(page), size: "20" });
    if (verdict) q.set("verdict", verdict);
    api<Page<Item>>(`/api/submissions?${q}`).then(setData).catch((e: Error) => setError(e.message));
  }, [verdict, page]);

  return (
    <>
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
          <table>
            <thead><tr><th>Problem</th><th>Status</th><th>Language</th><th className="th-num">Passed</th>
              <th className="th-num">Runtime</th><th className="th-num">Memory</th><th>Submitted</th></tr></thead>
            <tbody>
              {data.items.map((s) => (
                <tr key={s.id}>
                  <td>{s.slug ? <Link href={`/problems/${s.slug}`}>{s.title}</Link> : s.title}</td>
                  <td className={s.verdict}><b>{label(s.verdict)}</b></td>
                  <td>{s.language}</td>
                  <td className="th-num">{s.passed}/{s.total}</td>
                  <td className="th-num">{s.runtimeMs != null ? `${s.runtimeMs} ms` : "–"}</td>
                  <td className="th-num">{s.memoryKb != null ? `${(s.memoryKb / 1024).toFixed(1)} MB` : "–"}</td>
                  <td className="mute">{new Date(s.createdAt).toLocaleString()}</td>
                </tr>
              ))}
              {data.items.length === 0 && <tr><td colSpan={7} className="mute">No submissions yet.</td></tr>}
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
