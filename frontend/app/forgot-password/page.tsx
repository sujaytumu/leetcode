"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";
import { api } from "@/lib/api";
import { lastEmail } from "@/lib/auth";
import { usePageTitle } from "@/lib/usePageTitle";
import "../auth.css";

const COOLDOWN = 60;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** Asks for an email and always shows the same confirmation, so it cannot be used to find out who has an account. */
export default function ForgotPasswordPage() {
  usePageTitle("Forgot password");
  const [email, setEmail] = useState(() => (typeof window === "undefined" ? "" : lastEmail().includes("@") ? lastEmail() : ""));
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [touched, setTouched] = useState(false);
  const [mailOn, setMailOn] = useState<boolean | null>(null); // null = not known yet (server may be waking)
  const [wait, setWait] = useState(0);

  // Server-wide setting (not per account), so it reveals nothing about who has an account.
  useEffect(() => {
    api<{ enabled: boolean }>("/api/auth/mail-status", {}, 20000).then((r) => setMailOn(r.enabled)).catch(() => {});
  }, []);
  useEffect(() => {
    if (wait <= 0) return;
    const t = setTimeout(() => setWait((n) => n - 1), 1000);
    return () => clearTimeout(t);
  }, [wait]);

  const bad = touched && !EMAIL_RE.test(email.trim());

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy || wait > 0) return;
    setTouched(true);
    if (!EMAIL_RE.test(email.trim())) return;
    setBusy(true); setError("");
    try {
      await api("/api/auth/forgot", { method: "POST", body: JSON.stringify({ email: email.trim() }) }, 75000);
      setSent(true); setWait(COOLDOWN);
    } catch (err) { setError((err as Error).message); }
    setBusy(false);
  }

  return (
    <div className="authpage">
      <section className="card authcard">
        <div className="authlogo" style={{ display: "block" }}><Logo size={34} /></div>
        <h1 className="authtitle">Forgot your password?</h1>
        {mailOn === false && (
          <div className="banner warn" role="status">Password-reset email is not set up on this server yet, so no link can be sent. Please contact the site owner.</div>
        )}
        {sent ? (
          <>
            <p className="authsub">If an account exists for <b>{email.trim()}</b>, a reset link is on its way. It works for 30 minutes and only once.</p>
            <p className="mute authhint">Nothing yet? Check your spam folder.</p>
            <button type="button" className="authsubmit" disabled={wait > 0 || busy} onClick={() => setSent(false)}>
              {wait > 0 ? `Send again in ${wait}s` : "Send again"}
            </button>
            <p className="authswitch"><Link href="/login">Back to log in</Link></p>
          </>
        ) : (
          <>
            <p className="mute authsub">Enter the email you signed up with and we will send you a link to choose a new password.</p>
            <form onSubmit={submit} className="authform" noValidate>
              <label className="authfield"><span>Email</span>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} onBlur={() => setTouched(true)} autoComplete="email" inputMode="email" enterKeyHint="send"
                  placeholder="you@example.com" autoCapitalize="none" spellCheck={false} maxLength={254} required autoFocus aria-invalid={bad} aria-describedby={bad ? "fp-err" : undefined} />
                {bad && <span className="autherr" id="fp-err" role="alert">Enter a valid email address.</span>}
              </label>
              {error && <div className="banner err" role="alert">{error}</div>}
              <button className="primary authsubmit" disabled={busy || wait > 0 || mailOn === false}>
                {busy ? <><i className="authspin" aria-hidden="true" /> Sending…</> : wait > 0 ? `Send again in ${wait}s` : "Send reset link"}
              </button>
            </form>
            <p className="authswitch mute"><Link href="/login">Back to log in</Link></p>
          </>
        )}
      </section>
    </div>
  );
}
