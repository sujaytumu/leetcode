"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { AUTH_EVENT, authEmail, authToken, authUser, clearSession } from "@/lib/auth";

/**
 * Right end of the header: [Log in | Log out] then Profile. Profile is always the last item and always says
 * "Profile", so it stays at the same spot on every page and in every state. The signed-in name is only shown after a successful login.
 */
export default function AccountMenu() {
  const path = usePathname();
  const [user, setUser] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const sync = () => { const on = !!authToken(); setUser(on ? authUser() : null); setEmail(on ? authEmail() : null); };
    sync();
    window.addEventListener(AUTH_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => { window.removeEventListener(AUTH_EVENT, sync); window.removeEventListener("storage", sync); };
  }, []);

  return (
    <>
      {user
        ? <button type="button" className="nav-auth" onClick={() => { clearSession(); window.location.href = "/"; }}>Log out</button>
        : <Link href="/login" className={`nav-auth${(path.startsWith("/login") || path.startsWith("/register")) ? " active" : ""}`}>Log in</Link>}
      <Link href="/profile" className={`nav-profile${path.startsWith("/profile") ? " active" : ""}`}
        title={user ? `Signed in as ${email ?? user}` : "Your profile"} aria-label="Profile">
        <span aria-hidden="true">👤</span><span className="hide-sm"> {user ?? "Profile"}</span>
      </Link>
    </>
  );
}
