"use client";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Votes { likes: number; dislikes: number; myVote: "LIKE" | "DISLIKE" | null }

const compact = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}K` : String(n));

/** Like / dislike for a problem, one vote per browser, switchable and removable. */
export default function VoteButtons({ slug }: { slug: string }) {
  const [votes, setVotes] = useState<Votes | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let live = true;
    setVotes(null);
    api<Votes>(`/api/problems/${slug}/votes`).then((v) => { if (live) setVotes(v); }).catch(() => {});
    return () => { live = false; };
  }, [slug]);

  const cast = useCallback(async (type: "LIKE" | "DISLIKE") => {
    if (!votes || busy) return;
    setBusy(true);
    try {
      const next = votes.myVote === type
        ? await api<Votes>(`/api/problems/${slug}/vote`, { method: "DELETE" })
        : await api<Votes>(`/api/problems/${slug}/vote`, { method: "PUT", body: JSON.stringify({ vote: type }) });
      setVotes(next);
    } catch { /* leave the previous counts; the nav indicator covers connectivity */ }
    finally { setBusy(false); }
  }, [votes, busy, slug]);

  if (!votes) return null;
  return (
    <span className="votes">
      <button className={votes.myVote === "LIKE" ? "on" : ""} disabled={busy} onClick={() => cast("LIKE")}
        title={votes.myVote === "LIKE" ? "Remove your like" : "Like this problem"} aria-pressed={votes.myVote === "LIKE"}>
        👍 {compact(votes.likes)}
      </button>
      <button className={votes.myVote === "DISLIKE" ? "on" : ""} disabled={busy} onClick={() => cast("DISLIKE")}
        title={votes.myVote === "DISLIKE" ? "Remove your dislike" : "Dislike this problem"} aria-pressed={votes.myVote === "DISLIKE"}>
        👎 {compact(votes.dislikes)}
      </button>
    </span>
  );
}
