"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";
import "@/app/auth.css";
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

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** 0-4 from length and character variety. Display only; the server enforces the real rule (8+ characters). */
function strength(pw: string): number {
  if (!pw) return 0;
  let n = 0;
  if (pw.length >= 8) n++;
  if (pw.length >= 12) n++;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) n++;
  if (/\d/.test(pw) && /[^A-Za-z0-9]/.test(pw)) n++;
  return pw.length < 8 ? Math.min(n, 1) : Math.max(n, 1);
}
const STRENGTH_LABEL = ["", "Weak", "Fair", "Good", "Strong"];

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
  const [caps, setCaps] = useState(false);
  const [touched, setTouched] = useState({ id: false, pw: false });
  const router = useRouter();

  // Warm what comes next while the user types, so the first screen after logging in appears quickly.
  useEffect(() => {
    const next = nextPath();
    router.prefetch(next);
    if (next !== "/problemset") router.prefetch("/problemset");
  }, [router]);

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

  const idError = !touched.id ? "" : !id.trim() ? (register ? "Enter your email." : "Enter your email or username.") : register && !EMAIL_RE.test(id.trim()) ? "That doesn't look like a valid email." : "";
  const pwError = !touched.pw ? "" : !password ? "Enter your password." : register && password.length < 8 ? "Use at least 8 characters." : "";
  const score = register ? strength(password) : 0;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setTouched({ id: true, pw: true });
    if (!id.trim() || !password || (register && (!EMAIL_RE.test(id.trim()) || password.length < 8))) return;
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
    <div className="authpage authsplit">
      <aside className="authbrand" aria-hidden="true">
        <Logo size={44} />
        <h2>Practice. Solve. Get hired.</h2>
        <ul>
          <li><b>240+ problems</b> with optimal C++ solutions and editorials</li>
          <li><b>Striver A2Z, SDE &amp; Magic 50 sheets</b> with progress tracking</li>
          <li><b>Run &amp; Submit</b> in C++, Java, Python and JavaScript</li>
          <li><b>Streaks, contests</b> and spaced-repetition review</li>
        </ul>
      </aside>
      <section className="card authcard">
        <div className="authlogo"><Logo size={34} /></div>
        <h1 className="authtitle">{register ? "Create your account" : "Welcome back"}</h1>
        <p className="mute authsub">
          {register
            ? "Everything you have done in this browser (solves, bookmarks, notes) moves into your account."
            : "Log in to load your progress on this device. You stay signed in for 30 days."}
        </p>
        <form onSubmit={submit} className="authform" method="post" noValidate>
          <label className="authfield"><span>{register ? "Email" : "Email or username"}</span>
            <input name="email" id="email" type={register ? "email" : "text"} value={id} onChange={(e) => setId(e.target.value)} onBlur={() => setTouched((t) => ({ ...t, id: true }))}
              autoComplete={register ? "email" : "username"} inputMode={register ? "email" : "text"} enterKeyHint="next" placeholder={register ? "you@example.com" : "you@example.com or username"}
              autoCapitalize="none" autoCorrect="off" spellCheck={false} maxLength={254} required autoFocus={!id}
              aria-invalid={!!idError} aria-describedby={idError ? "email-err" : undefined} />
            {idError && <span className="autherr" id="email-err" role="alert">{idError}</span>}
          </label>
          <label className="authfield"><span>Password</span>
            <span className="passwrap">
              <input name="password" id="password" type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} onBlur={() => setTouched((t) => ({ ...t, pw: true }))}
                onKeyUp={(e) => setCaps(e.getModifierState?.("CapsLock") ?? false)} enterKeyHint="go"
                autoComplete={register ? "new-password" : "current-password"} maxLength={72} required
                aria-invalid={!!pwError} aria-describedby={pwError ? "pw-err" : undefined} />
              <button type="button" className="passtoggle" onClick={() => setShow((v) => !v)} aria-label={show ? "Hide password" : "Show password"} aria-pressed={show}>
                {show ? "Hide" : "Show"}
              </button>
            </span>
            {caps && <span className="authwarn" role="status">Caps Lock is on</span>}
            {pwError && <span className="autherr" id="pw-err" role="alert">{pwError}</span>}
          </label>
          {register && (
            <div className="strength" aria-live="polite">
              <div className={`strength-bar s${score}`}><i /><i /><i /><i /></div>
              <span className="mute authhint">{password ? `${STRENGTH_LABEL[score]} password` : "Password 8+ characters."} Your display name is created from the email and can be changed in your profile.</span>
            </div>
          )}
          {!register && (
            <div className="authrow"><span /><Link href="/forgot-password" className="authhint">Forgot password?</Link></div>
          )}
          {register && (
            <label className="authcheck"><input type="checkbox" checked={daily} onChange={(e) => setDaily(e.target.checked)} /> Email me one problem every morning (you can stop it any time)</label>
          )}
          {error && <div className="banner err" role="alert">{error}</div>}
          <button className="primary authsubmit" disabled={busy}>
            {busy ? <><i className="authspin" aria-hidden="true" /> Please wait…</> : register ? "Create account" : "Log in"}
          </button>
          {slow && <span className="mute authhint" role="status">The server is waking up. This can take up to a minute the first time.</span>}
        </form>
        <p className="authswitch mute">
          {register ? <>Already have an account? <Link href="/login">Log in</Link></> : <>New here? <Link href="/register">Create an account</Link></>}
        </p>
        <p className="authguest mute"><Link href="/problemset">Continue without an account →</Link></p>
      </section>
    </div>
  );
}
