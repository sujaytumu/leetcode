"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Session, setSession } from "@/lib/auth";
import Logo from "@/components/Logo";
import { usePageTitle } from "@/lib/usePageTitle";
import "../auth.css";

/** Landing page of the emailed link: choose a new password, then you are signed in. */
export default function ResetPasswordPage() {
  usePageTitle("Reset password");
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [again, setAgain] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const score = (() => {
    if (!password) return 0;
    let n = 0;
    if (password.length >= 8) n++;
    if (password.length >= 12) n++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) n++;
    if (/\d/.test(password) && /[^A-Za-z0-9]/.test(password)) n++;
    return password.length < 8 ? Math.min(n, 1) : Math.max(n, 1);
  })();

  useEffect(() => { setToken(new URLSearchParams(window.location.search).get("token") ?? ""); }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    if (password.length < 8 || password.length > 72) { setError("Password must be 8-72 characters."); return; }
    if (password !== again) { setError("The two passwords do not match."); return; }
    setBusy(true); setError("");
    try {
      const s = await api<Session>("/api/auth/reset", { method: "POST", body: JSON.stringify({ token, password }) }, 75000);
      setSession(s);
      window.location.replace("/");
    } catch (err) { setError((err as Error).message); setBusy(false); }
  }

  if (token === null) return null;
  return (
    <div className="authpage">
      <section className="card authcard">
        <div className="authlogo" style={{ display: "block" }}><Logo size={34} /></div>
        <h1 className="authtitle">Choose a new password</h1>
        {!token ? (
          <>
            <div className="banner err">This page needs the link from your email.</div>
            <p className="authswitch"><Link href="/forgot-password">Request a new link</Link></p>
          </>
        ) : (
          <form onSubmit={submit} className="authform">
            <label className="authfield"><span>New password</span>
              <span className="passwrap">
                <input type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" minLength={8} maxLength={72} required autoFocus />
                <button type="button" className="passtoggle" onClick={() => setShow((v) => !v)} aria-label={show ? "Hide password" : "Show password"}>{show ? "Hide" : "Show"}</button>
              </span>
            </label>
            <label className="authfield"><span>Repeat new password</span>
              <input type={show ? "text" : "password"} value={again} onChange={(e) => setAgain(e.target.value)} autoComplete="new-password" maxLength={72} required />
            </label>
            <div className="strength" aria-live="polite">
              <div className={`strength-bar s${score}`}><i /><i /><i /><i /></div>
              <span className="mute authhint">{password ? `${["", "Weak", "Fair", "Good", "Strong"][score]} password. ` : ""}8+ characters. This signs out your other devices.</span>
            </div>
            {error && (
              <div className="banner err" role="alert">{error} {/expired|invalid/i.test(error) && <Link href="/forgot-password">Request a new link</Link>}</div>
            )}
            <button className="primary authsubmit" disabled={busy || !password || !again}>{busy ? "Please wait…" : "Set password and log in"}</button>
          </form>
        )}
      </section>
    </div>
  );
}
