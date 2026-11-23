"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, clientId } from "@/lib/api";
import { authEmail, authToken, authUser } from "@/lib/auth";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

interface Board { me: { rank: number; points: number; solved: number } | null; participants: number }

/** Global rank plus a sync code: progress lives under an anonymous id, so entering the same code on another device restores it. */
export default function SyncCard() {
  const [code, setCode] = useState("");
  const [board, setBoard] = useState<Board | null>(null);
  const [entered, setEntered] = useState("");
  const [msg, setMsg] = useState("");
  const [user, setUser] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    setCode(clientId());
    setUser(authToken() ? authUser() : null);
    setEmail(authToken() ? authEmail() : null);
    api<Board>("/api/leaderboard?limit=1").then(setBoard).catch(() => {});
  }, []);

  async function copy() {
    try { await navigator.clipboard.writeText(code); setMsg("Copied. Keep it private: anyone with it can use your progress."); }
    catch { setMsg("Could not copy automatically. Select the code and copy it by hand."); }
  }

  function restore() {
    const next = entered.trim().toLowerCase();
    if (!UUID.test(next)) { setMsg("That is not a valid sync code."); return; }
    if (next === code) { setMsg("This device already uses that code."); return; }
    if (!window.confirm("Switch this browser to that sync code? The progress currently shown here stays on this device's old code.")) return;
    try {
      localStorage.setItem("lc-client-id", next);
      Object.keys(localStorage).filter((k) => k.startsWith("lc-cache:")).forEach((k) => localStorage.removeItem(k));
    } catch { setMsg("Could not save: browser storage is blocked."); return; }
    window.location.reload();
  }

  return (
    <section className="card synccard">
      <h3 style={{ margin: "0 0 8px" }}>Ranking &amp; sync</h3>
      <p style={{ margin: "0 0 10px" }}>
        {board?.me
          ? <>Global rank <b style={{ display: "inline", fontSize: 16 }}>#{board.me.rank}</b> of {board.participants} · {board.me.points} points · </>
          : <span className="mute">Solve a problem to get a global rank. </span>}
        <Link href="/leaderboard">View leaderboard</Link> · <Link href="/submissions">My submissions</Link> · <Link href="/stats">My stats</Link>
      </p>
      {user ? (
        <p className="mute" style={{ margin: 0 }}>Signed in as <b style={{ display: "inline", fontSize: 14 }}>{email ?? user}</b>. Log in on any device to get this progress; no sync code needed. <Link href="/account">Account settings</Link></p>
      ) : (<>
      <p className="mute" style={{ margin: "0 0 10px" }}><Link href="/register">Create an account</Link> to protect this progress with a password. A sync code lets anyone who has it use your progress.</p>
      <div className="iolabel">Your sync code</div>
      <div className="bar" style={{ flexWrap: "wrap" }}>
        <code style={{ overflowWrap: "anywhere" }}>{code}</code>
        <button onClick={copy}>Copy</button>
      </div>
      <div className="iolabel" style={{ marginTop: 10 }}>Use a code from another device</div>
      <div className="bar" style={{ flexWrap: "wrap" }}>
        <input value={entered} placeholder="paste sync code" onChange={(e) => setEntered(e.target.value)} style={{ flex: 1, minWidth: 220 }} />
        <button disabled={!entered.trim()} onClick={restore}>Restore</button>
      </div>
      </>)}
      {msg && <p className="mute" style={{ margin: "8px 0 0" }}>{msg}</p>}
    </section>
  );
}
