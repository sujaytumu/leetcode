"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { usePageTitle } from "@/lib/usePageTitle";

/** One-click unsubscribe from the link in a daily email. Needs no login. */
export default function UnsubscribePage() {
  usePageTitle("Unsubscribe");
  const [state, setState] = useState<"working" | "done" | "error">("working");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) { setError("This link is missing its token."); setState("error"); return; }
    api("/api/auth/unsubscribe", { method: "POST", body: JSON.stringify({ token }) }, 75000)
      .then(() => setState("done"))
      .catch((e: Error) => { setError(e.message); setState("error"); });
  }, []);

  return (
    <div className="authpage">
      <section className="card authcard">
        <h1 className="authtitle">Daily email</h1>
        {state === "working" && <p className="mute authsub">Updating your preference…</p>}
        {state === "done" && <p className="authsub">You are unsubscribed. You can turn the daily problem email back on any time in <Link href="/account">Account settings</Link>.</p>}
        {state === "error" && <div className="banner err">{error}</div>}
      </section>
    </div>
  );
}
