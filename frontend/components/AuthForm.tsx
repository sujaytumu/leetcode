"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { authToken, Session, setSession } from "@/lib/auth";

type Mode = "login" | "register";
const LAST_USER = "lc-last-email";

/** Only same-site paths: stops "?next=https://evil" from bouncing a freshly logged-in user off-site. */
function nextPath(): string {
  try {
    const n = new URLSearchParams(window.location.search).get("next");
    return n && n.startsWith("/") && !n.startsWith("//") && !n.startsWith("/login") && !n.startsWith("/register") ? n : "/";
  } catch { return "/"; }
}

/** One focused form per page (/login, /register). On success the user lands on the main page. */
export default function AuthForm({ mode }: { mode: Mode }) {
  const register = mode === "register";
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [daily, setDaily] = useState(false);
  const [busy, setBusy] = useState(false);
  const [slow, setSlow] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Already signed in: nothing to do here.
    if (authToken()) { window.location.replace(nextPath()); return; }
    try { const u = localStorage.getItem(LAST_USER); if (u && !register) setId(u); } catch { /* storage blocked */ }
  }, [register]);

  useEffect(() => {
    if (!busy) { setSlow(false); return; }
    const t = setTimeout(() => setSlow(true), 6000);
    return () => clearTimeout(t);
  }, [busy]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true); setError("");
    const name = id.trim();
    try {
      // The free-tier server can take about a minute to wake up, so allow for that.
      const s = await api<Session>(`/api/auth/${mode}`, { method: "POST", body: JSON.stringify(register ? { email: name, password, dailyEmail: daily } : { email: name, password }) }, 75000);
      try { localStorage.setItem(LAST_USER, name); } catch { /* storage blocked */ }
      setSession(s);
      window.location.replace(nextPath());
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <div className="authpage">
      <section className="card authcard">
        <h1 className="authtitle">{register ? "Create your account" : "Welcome back"}</h1>
        <p className="mute authsub">
          {register
            ? "Everything you have done in this browser (solves, bookmarks, notes) moves into your account."
            : "Log in to load your progress on this device. You stay signed in for 30 days."}
        </p>
        <form onSubmit={submit} className="authform" method="post">
          <label className="authfield"><span>{register ? "Email" : "Email or username"}</span>
            <input name="email" id="email" type={register ? "email" : "text"} value={id} onChange={(e) => setId(e.target.value)} autoComplete={register ? "email" : "username"}
              autoCapitalize="none" autoCorrect="off" spellCheck={false} maxLength={254} required autoFocus={!id} />
          </label>
          <label className="authfield"><span>Password</span>
            <span className="passwrap">
              <input name="password" id="password" type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)}
                autoComplete={register ? "new-password" : "current-password"} minLength={register ? 8 : undefined} maxLength={72} required />
              <button type="button" className="passtoggle" onClick={() => setShow((v) => !v)} aria-label={show ? "Hide password" : "Show password"}>
                {show ? "Hide" : "Show"}
              </button>
            </span>
          </label>
          {register && <span className="mute authhint">Password 8+ characters. Your display name is created from the email and can be changed in your profile.</span>}
          {register && (
            <label className="authcheck"><input type="checkbox" checked={daily} onChange={(e) => setDaily(e.target.checked)} /> Email me one problem every morning (you can stop it any time)</label>
          )}
          {error && <div className="banner err" role="alert">{error}</div>}
          <button className="primary authsubmit" disabled={busy || !id.trim() || !password}>
            {busy ? "Please wait…" : register ? "Create account" : "Log in"}
          </button>
          {slow && <span className="mute authhint" role="status">The server is waking up. This can take up to a minute the first time.</span>}
        </form>
        <p className="authswitch mute">
          {register ? <>Already have an account? <Link href="/login">Log in</Link></> : <>New here? <Link href="/register">Create an account</Link></>}
        </p>
        {!register && (
          <p className="authhint" style={{ margin: "10px 0 0", textAlign: "center" }}><Link href="/forgot-password">Forgot your password?</Link></p>
        )}
      </section>
    </div>
  );
}
