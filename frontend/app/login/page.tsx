"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { Session, setSession } from "@/lib/auth";

type Mode = "login" | "register";

/** Log in, or create an account that adopts this browser's progress so far. */
export default function LoginPage() {
  const [mode, setMode] = useState<Mode>("register");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true); setError("");
    try {
      const s = await api<Session>(`/api/auth/${mode}`, { method: "POST", body: JSON.stringify({ username, password }) });
      setSession(s);
      window.location.href = "/profile";
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  const register = mode === "register";
  return (
    <section className="card authcard">
      <div className="bar" style={{ marginBottom: 12 }}>
        <button type="button" className={register ? "on" : ""} onClick={() => { setMode("register"); setError(""); }}>Create account</button>
        <button type="button" className={!register ? "on" : ""} onClick={() => { setMode("login"); setError(""); }}>Log in</button>
      </div>
      <p className="mute" style={{ margin: "0 0 12px", fontSize: 13 }}>
        {register
          ? "Everything you have done in this browser (solves, bookmarks, notes) moves into your account."
          : "Logging in loads your account's progress here. Anything done while logged out on this browser stays on that anonymous profile."}
      </p>
      <form onSubmit={submit} style={{ display: "grid", gap: 10 }}>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" autoComplete="username"
          autoCapitalize="none" spellCheck={false} maxLength={20} required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password"
          autoComplete={register ? "new-password" : "current-password"} minLength={register ? 8 : undefined} maxLength={72} required />
        {register && <span className="mute" style={{ fontSize: 12 }}>3-20 letters, digits or underscores. Password 8+ characters.</span>}
        {error && <div className="banner err">{error}</div>}
        <button className="primary" disabled={busy || !username.trim() || !password}>
          {busy ? "Please wait…" : register ? "Create account" : "Log in"}
        </button>
      </form>
    </section>
  );
}
