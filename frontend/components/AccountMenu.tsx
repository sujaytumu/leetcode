"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api, ProfileInfo } from "@/lib/api";
import { AUTH_EVENT, authToken, authUser, clearSession } from "@/lib/auth";

const initials = (name: string) => name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("") || "?";

/**
 * Right end of the header. Signed out: a Log in link. Signed in: a small round avatar; clicking it opens a LeetCode-style
 * menu with your name and username, then Profile, Submissions, Notes, Lists, Account and Log out.
 */
export default function AccountMenu() {
  const path = usePathname();
  const [user, setUser] = useState<string | null>(null);
  const [info, setInfo] = useState<ProfileInfo | null>(null);
  const [photoOk, setPhotoOk] = useState(true);
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sync = () => { setUser(authToken() ? authUser() : null); };
    sync();
    window.addEventListener(AUTH_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => { window.removeEventListener(AUTH_EVENT, sync); window.removeEventListener("storage", sync); };
  }, []);

  useEffect(() => {
    if (!user) { setInfo(null); return; }
    api<ProfileInfo>("/api/profile/info").then(setInfo).catch(() => {});
  }, [user]);

  useEffect(() => { setOpen(false); }, [path]);
  useEffect(() => {
    if (!open) return;
    const away = (e: MouseEvent) => { if (box.current && !box.current.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", esc); };
  }, [open]);

  if (!user) {
    return <Link href="/login" className={`nav-auth${(path.startsWith("/login") || path.startsWith("/register")) ? " active" : ""}`}>Log in</Link>;
  }

  const name = info?.displayName || user;
  const handle = info?.username || user;
  const avatar = (cls: string) => info?.github && photoOk
    // eslint-disable-next-line @next/next/no-img-element
    ? <img className={cls} src={`https://github.com/${info.github}.png?size=96`} alt="" onError={() => setPhotoOk(false)} />
    : <span className={cls} aria-hidden="true">{initials(name)}</span>;

  return (
    <div className="acctmenu" ref={box}>
      <button type="button" className={`acct-btn${(path === "/" || path.startsWith("/profile")) ? " active" : ""}`} aria-label="Account menu" aria-haspopup="menu" aria-expanded={open}
        onClick={() => setOpen((v) => !v)}>
        {avatar("acct-av")}
      </button>
      {open && (
        <div className="acct-pop" role="menu">
          <Link href="/" className="acct-head" role="menuitem">
            {avatar("acct-av lg")}
            <span><b>{name}</b><span className="mute">{handle}</span></span>
          </Link>
          <Link href="/" role="menuitem">Profile</Link>
          <Link href="/submissions" role="menuitem">Submissions</Link>
          <Link href="/notes" role="menuitem">Notes</Link>
          <Link href="/lists" role="menuitem">My Lists</Link>
          <Link href="/account" role="menuitem">Account Settings</Link>
          <hr />
          <button type="button" role="menuitem" onClick={() => { clearSession(); window.location.href = "/"; }}>Log out</button>
        </div>
      )}
    </div>
  );
}
