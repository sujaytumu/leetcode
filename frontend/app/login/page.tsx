"use client";
import { usePageTitle } from "@/lib/usePageTitle";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { lastEmail, Session, setSession } from "@/lib/auth";

type Mode = "login" | "register";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** Sign up or log in with email + password. Signing up adopts this browser's progress so far. */
export default function LoginPage() {
  usePageTitle("Log in");
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { setEmail(lastEmail()); }, []);

  const register = mode === "register";
  const emailOk = EMAIL_RE.test(email.trim());
  const pwOk = password.length >= 8 && password.length <= 72;
  const matchOk = !register || password === confirm;
  const ready = emailOk && (register ? pwOk && matchOk : password.length > 0);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy || !ready) return;
    setBusy(true); setError("");
    try {
      const s = await api<Session>(`/api/auth/${mode}`, { method: "POST", body: JSON.stringify({ email: email.trim(), password }) });
      setSession(s);
      window.location.href = "/profile";
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <section className="card authcard">
      <div className="bar" style={{ marginBottom: 12 }}>
        <button type="button" className={!register ? "on" : ""} onClick={() => { setMode("login"); setError(""); }}>Log in</button>
        <button type="button" className={register ? "on" : ""} onClick={() => { setMode("register"); setError(""); }}>Create account</button>
      </div>
      <p className="mute" style={{ margin: "0 0 12px", fontSize: 13 }}>
        {register
          ? "Everything you have done in this browser (solves, bookmarks, notes) moves into your account."
          : "You stay signed in on this device. Log in on any other device to get your progress there."}
      </p>
      <form onSubmit={submit} style={{ display: "grid", gap: 10 }}>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" autoComplete="email"
          autoCapitalize="none" spellCheck={false} maxLength={254} required />
        <div className="bar">
          <input className="grow" type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)}
            placeholder="Password" autoComplete={register ? "new-password" : "current-password"} maxLength={72} required />
          <button type="button" onClick={() => setShow((v) => !v)} aria-label={show ? "Hide password" : "Show password"}>{show ? "Hide" : "Show"}</button>
        </div>
        {register && (
          <input type={show ? "text" : "password"} value={confirm} onChange={(e) => setConfirm(e.target.value)}
            placeholder="Confirm password" autoComplete="new-password" maxLength={72} required />
        )}
        {register && <span className="mute" style={{ fontSize: 12 }}>
          Password 8-72 characters{password && !pwOk ? " (too short)" : ""}{confirm && !matchOk ? ". Passwords do not match." : "."}
        </span>}
        {error && <div className="banner err">{error}</div>}
        <button className="primary" disabled={busy || !ready}>
          {busy ? "Please wait…" : register ? "Create account" : "Log in"}
        </button>
      </form>
    </section>
  );
}
