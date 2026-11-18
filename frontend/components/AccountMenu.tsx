"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AUTH_EVENT, authToken, authUser, clearSession } from "@/lib/auth";

/** "Log in" when signed out; username + "Log out" when signed in. Read after mount so SSR and first paint match. */
export default function AccountMenu() {
  const [user, setUser] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const sync = () => setUser(authToken() ? authUser() : null);
    sync(); setReady(true);
    window.addEventListener(AUTH_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => { window.removeEventListener(AUTH_EVENT, sync); window.removeEventListener("storage", sync); };
  }, []);

  if (!ready) return null;
  if (!user) return <Link href="/login">Log in</Link>;
  return (
    <>
      <Link href="/profile" title="Your profile">👤 {user}</Link>
      <button type="button" onClick={() => { clearSession(); window.location.href = "/"; }}>Log out</button>
    </>
  );
}
