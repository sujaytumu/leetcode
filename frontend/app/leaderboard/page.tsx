"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import { useEffect, useState } from "react";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";

interface Entry { rank: number; name: string; easy: number; medium: number; hard: number; solved: number; points: number; you: boolean }
interface Community { accounts: number; coders: number; submissions: number }
interface Board { top: Entry[]; me: Entry | null; participants: number }

const medal = (rank: number) => (rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : String(rank));

export default function LeaderboardPage() {
  usePageTitle("Leaderboard");
  const [board, setBoard] = useState<Board | null>(null);
  const [error, setError] = useState("");
  const [community, setCommunity] = useState<Community | null>(null);

  useEffect(() => {
    swr<Board>("/api/leaderboard?limit=50", setBoard, () => {}).catch((e: Error) => setError(e.message));
    swr<Community>("/api/community", setCommunity, () => {}).catch(() => undefined);
  }, []);

  const row = (e: Entry) => (
    <tr key={e.rank} className={e.you ? "me-row" : ""}>
      <td className="th-num">{medal(e.rank)}</td>
      <td><b>{e.name}</b>{e.you && <span className="pill MEDIUM" style={{ marginLeft: 6 }}>you</span>}</td>
      <td className="th-num col-emh"><span className="EASY">{e.easy}</span> / <span className="MEDIUM">{e.medium}</span> / <span className="HARD">{e.hard}</span></td>
      <td className="th-num">{e.solved}</td>
      <td className="th-num"><b>{e.points}</b></td>
    </tr>
  );

  return (
    <>
      <span className="narrowmark" hidden />
      <h2 style={{ marginBottom: 4 }}>Leaderboard</h2>
      <p className="mute" style={{ marginTop: 0 }}>
        Ranked by points: Easy 10, Medium 20, Hard 40 for each problem you have solved. Set a username on your profile to show a name.
      </p>
      {community && (
        <div className="statchips" aria-label="Community totals">
          <span><b>{community.coders}</b> {community.coders === 1 ? "coder" : "coders"}</span>
          <span><b>{community.accounts}</b> {community.accounts === 1 ? "account" : "accounts"}</span>
          <span><b>{community.submissions}</b> {community.submissions === 1 ? "submission" : "submissions"}</span>
        </div>
      )}
      {error && <div className="banner err">{error}</div>}
      {!board && !error && <Skeleton />}
      {board && (
        <>
          <p className="mute">{board.participants} {board.participants === 1 ? "solver" : "solvers"} ranked
            {board.me ? <> · you are <b>#{board.me.rank}</b> with {board.me.points} points</> : " · solve a problem to join the ranking"}</p>
          <div className="tscroll"><table>
            <thead><tr><th className="th-num" style={{ width: 56 }}>Rank</th><th>User</th>
              <th className="th-num col-emh">Easy / Med / Hard</th><th className="th-num">Solved</th><th className="th-num">Points</th></tr></thead>
            <tbody>
              {board.top.map(row)}
              {board.me && !board.top.some((e) => e.you) && (
                <>
                  <tr><td colSpan={5} className="mute" style={{ textAlign: "center" }}>⋯</td></tr>
                  {row(board.me)}
                </>
              )}
              {board.top.length === 0 && <tr><td colSpan={5} className="mute">Nobody has solved a problem yet. Be the first.</td></tr>}
            </tbody>
          </table></div>
        </>
      )}
    </>
  );
}
