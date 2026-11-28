"use client";
import BackLink from "@/components/BackLink";
import { usePageTitle } from "@/lib/usePageTitle";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { authEmail, authToken, authUser, clearSession, Session, setSession } from "@/lib/auth";

/** Account settings: who you are signed in as, change password, log out. Visible only after a successful login. */
export default function AccountPage() {
  usePageTitle("Account");
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState("");
  const [email, setEmail] = useState("");
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [again, setAgain] = useState("");
  const [busy, setBusy] = useState(false);
  const [daily, setDaily] = useState<boolean | null>(null);
  const [dailyBusy, setDailyBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  useEffect(() => {
    if (!authToken()) { window.location.replace("/login"); return; }
    setUser(authUser() ?? ""); setEmail(authEmail() ?? ""); setReady(true);
    api<{ email: string | null; dailyEmail: boolean }>("/api/auth/email-prefs").then((p) => setDaily(p.dailyEmail)).catch(() => setDaily(null));
  }, []);

  async function change(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    if (next.length < 8 || next.length > 72) { setMsg({ ok: false, text: "New password must be 8-72 characters." }); return; }
    if (next !== again) { setMsg({ ok: false, text: "New passwords do not match." }); return; }
    setBusy(true); setMsg(null);
    try {
      // Changing the password revokes old tokens; the response carries a fresh one for this device.
      const s = await api<Session>("/api/auth/password", { method: "POST", body: JSON.stringify({ currentPassword: current, newPassword: next }) });
      setSession(s);
      setCurrent(""); setNext(""); setAgain("");
      setMsg({ ok: true, text: "Password changed. Other devices will ask you to log in again." });
    } catch (err) { setMsg({ ok: false, text: (err as Error).message }); }
    setBusy(false);
  }

  async function toggleDaily(on: boolean) {
    if (dailyBusy) return;
    setDailyBusy(true);
    try {
      const p = await api<{ dailyEmail: boolean }>("/api/auth/email-prefs", { method: "PUT", body: JSON.stringify({ dailyEmail: on }) });
      setDaily(p.dailyEmail);
    } catch (err) { setMsg({ ok: false, text: (err as Error).message }); }
    setDailyBusy(false);
  }

  async function signOutOthers() {
    if (busy) return;
    setBusy(true); setMsg(null);
    try {
      const s = await api<Session>("/api/auth/logout-all", { method: "POST" });
      setSession(s);
      setMsg({ ok: true, text: "Signed out of every other device." });
    } catch (err) { setMsg({ ok: false, text: (err as Error).message }); }
    setBusy(false);
  }

  if (!ready) return null;
  return (
    <section className="card authcard" style={{ maxWidth: 440 }}>
      <h2 style={{ margin: "0 0 10px" }}>Account</h2>
      <div className="acct-rows">
        <div><span className="mute">Name</span><b>{user}</b></div>
        <div><span className="mute">Email</span><b>{email || "not set (log in with your username)"}</b></div>
      </div>
      {email && daily !== null && (
        <label className="authcheck" style={{ marginTop: 14 }}>
          <input type="checkbox" checked={daily} disabled={dailyBusy} onChange={(e) => toggleDaily(e.target.checked)} />
          Email me the daily problem every morning
        </label>
      )}
      <h3 style={{ margin: "18px 0 8px" }}>Change password</h3>
      <form onSubmit={change} style={{ display: "grid", gap: 10 }}>
        <input type="password" value={current} onChange={(e) => setCurrent(e.target.value)} placeholder="Current password" autoComplete="current-password" maxLength={72} required />
        <input type="password" value={next} onChange={(e) => setNext(e.target.value)} placeholder="New password" autoComplete="new-password" maxLength={72} required />
        <input type="password" value={again} onChange={(e) => setAgain(e.target.value)} placeholder="Repeat new password" autoComplete="new-password" maxLength={72} required />
        {msg && <div className={`banner ${msg.ok ? "" : "err"}`}>{msg.text}</div>}
        <button className="primary" disabled={busy || !current || !next || !again}>{busy ? "Please wait…" : "Change password"}</button>
      </form>
      <h3 style={{ margin: "18px 0 6px" }}>Devices</h3>
      <p className="mute" style={{ margin: "0 0 8px", fontSize: 13 }}>Lost a phone or used a shared computer? Sign out everywhere else. You stay signed in here.</p>
      <button type="button" onClick={signOutOthers} disabled={busy}>Sign out other devices</button>
      <div className="bar" style={{ marginTop: 16 }}>
        <BackLink fallback="/profile" /><span className="grow" />
        <button type="button" onClick={() => { clearSession(); window.location.href = "/"; }}>Log out</button>
      </div>
    </section>
  );
}
