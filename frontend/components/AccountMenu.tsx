"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { api, ProfileInfo } from "@/lib/api";
import { AUTH_EVENT, authToken, authUser, clearSession } from "@/lib/auth";
import { ACCENT_KEY, ACCENTS, accentByKey, saveAccent } from "@/lib/appearance";
import { currentTheme, type ThemeName } from "@/components/ThemeToggle";

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
  const [accent, setAccent] = useState("amber");
  const [theme, setTheme] = useState<ThemeName>("dark");
  useEffect(() => {
    if (!open) return;
    try { setAccent(accentByKey(localStorage.getItem(ACCENT_KEY))?.key ?? "amber"); } catch { /* storage blocked */ }
    setTheme(currentTheme());
  }, [open]);
  const pickTheme = (t: ThemeName) => {
    document.documentElement.dataset.theme = t;
    try { localStorage.setItem("lc-theme", t); } catch { /* storage blocked */ }
    window.dispatchEvent(new Event("lc-theme"));
    setTheme(t);
  };

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
  const home = info?.username ? `/${encodeURIComponent(info.username)}` : "/";
  const avatar = (cls: string) => info?.github && photoOk
    // eslint-disable-next-line @next/next/no-img-element
    ? <img className={cls} src={`https://github.com/${info.github}.png?size=96`} alt="" onError={() => setPhotoOk(false)} />
    : <span className={cls} aria-hidden="true">{initials(name)}</span>;

  return (
    <div className="acctmenu" ref={box}>
      <button type="button" className={`acct-btn${(path === "/" || path === home || path.startsWith("/profile")) ? " active" : ""}`} aria-label="Account menu" aria-haspopup="menu" aria-expanded={open}
        onClick={() => setOpen((v) => !v)}>
        {avatar("acct-av")}
      </button>
      {open && (
        <div className="acct-pop" role="menu">
          <Link href={home} className="acct-head" role="menuitem">
            {avatar("acct-av lg")}
            <span><b>{name}</b><span className="mute">{handle}</span></span>
          </Link>
          <Link href={home} role="menuitem">Profile</Link>
          <Link href="/submissions" role="menuitem">Submissions</Link>
          <Link href="/notes" role="menuitem">Notes</Link>
          <Link href="/lists" role="menuitem">My Lists</Link>
          <Link href="/settings/profile" role="menuitem">Profile Settings</Link>
          <Link href="/account" role="menuitem">Account Settings</Link>
          <hr />
          <div className="acct-appear" aria-label="Appearance">
            <div className="acct-row"><span>Theme</span>
              <span className="acct-seg" role="radiogroup" aria-label="Theme">
                {(["dark", "light"] as ThemeName[]).map((t) => (
                  <button key={t} type="button" role="radio" aria-checked={theme === t} className={theme === t ? "on" : ""} onClick={() => pickTheme(t)}>{t === "dark" ? "Dark" : "Light"}</button>
                ))}
              </span>
            </div>
            <div className="acct-row"><span>Accent</span>
              <span className="swatches" role="radiogroup" aria-label="Accent colour">
                {ACCENTS.map((a) => (
                  <button key={a.key} type="button" role="radio" aria-checked={accent === a.key} aria-label={a.label} title={a.label}
                    className={`swatch${accent === a.key ? " on" : ""}`} style={{ background: a.dark }}
                    onClick={() => { setAccent(a.key); saveAccent(a); }} />
                ))}
              </span>
            </div>
          </div>
          <hr />
          <button type="button" role="menuitem" onClick={() => { clearSession(); window.location.href = "/"; }}>Log out</button>
        </div>
      )}
    </div>
  );
}
