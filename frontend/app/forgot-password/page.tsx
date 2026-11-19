"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { lastEmail } from "@/lib/auth";
import { usePageTitle } from "@/lib/usePageTitle";

/** Asks for an email and always shows the same confirmation, so it cannot be used to find out who has an account. */
export default function ForgotPasswordPage() {
  usePageTitle("Forgot password");
  const [email, setEmail] = useState(() => (typeof window === "undefined" ? "" : lastEmail().includes("@") ? lastEmail() : ""));
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true); setError("");
    try {
      await api("/api/auth/forgot", { method: "POST", body: JSON.stringify({ email: email.trim() }) }, 75000);
      setSent(true);
    } catch (err) { setError((err as Error).message); }
    setBusy(false);
  }

  return (
    <div className="authpage">
      <section className="card authcard">
        <h1 className="authtitle">Forgot your password?</h1>
        {sent ? (
          <>
            <p className="authsub">If an account exists for <b>{email.trim()}</b>, a reset link is on its way. It works for 30 minutes and only once.</p>
            <p className="mute authhint">Nothing yet? Check spam, or try again in a minute.</p>
            <p className="authswitch"><Link href="/login">Back to log in</Link></p>
          </>
        ) : (
          <>
            <p className="mute authsub">Enter the email you signed up with and we will send you a link to choose a new password.</p>
            <form onSubmit={submit} className="authform">
              <label className="authfield"><span>Email</span>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" autoCapitalize="none"
                  spellCheck={false} maxLength={254} required autoFocus />
              </label>
              {error && <div className="banner err" role="alert">{error}</div>}
              <button className="primary authsubmit" disabled={busy || !email.trim()}>{busy ? "Sending…" : "Send reset link"}</button>
            </form>
            <p className="authswitch mute"><Link href="/login">Back to log in</Link></p>
          </>
        )}
      </section>
    </div>
  );
}
