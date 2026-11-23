"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const TABS = [
  { href: "/", label: "Problems", icon: "☰" },
  { href: "/plans", label: "Plans", icon: "🗺" },
  { href: "/daily", label: "Daily", icon: "📅" },
  { href: "/contest", label: "Contest", icon: "🏆" },
];
const MORE = [
  { href: "/topics", label: "Topics" }, { href: "/for-you", label: "For you" }, { href: "/practice", label: "Practice" },
  { href: "/review", label: "Review" }, { href: "/notes", label: "Notes" }, { href: "/lists", label: "Lists" },
  { href: "/mock", label: "Mock interview" }, { href: "/leaderboard", label: "Ranking" }, { href: "/playground", label: "Playground" },
  { href: "/stats", label: "My stats" }, { href: "/profile", label: "Profile" }, { href: "/account", label: "Account" }, { href: "/settings/profile", label: "Settings" },
];

const active = (path: string, href: string) => (href === "/" ? path === "/" : path === href || path.startsWith(`${href}/`));

/** Phone-only bottom navigation (hidden by CSS above 700px). The problem workspace has its own action bar, so it is hidden there. */
export default function MobileTabBar() {
  const path = usePathname() ?? "/";
  const [more, setMore] = useState(false);
  useEffect(() => { setMore(false); }, [path]);
  useEffect(() => {
    if (!more) return;
    const h = (e: KeyboardEvent) => { if (e.key === "Escape") setMore(false); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [more]);
  if (path.startsWith("/problems/")) return null;
  const inMore = MORE.some((m) => active(path, m.href));
  return (
    <>
      {more && (
        <div className="msheet-backdrop" onClick={() => setMore(false)}>
          <div className="msheet" role="dialog" aria-label="More pages" onClick={(e) => e.stopPropagation()}>
            <div className="msheet-grip" aria-hidden="true" />
            <div className="msheet-grid">
              {MORE.map((m) => <Link key={m.href} href={m.href} className={active(path, m.href) ? "on" : ""}>{m.label}</Link>)}
            </div>
          </div>
        </div>
      )}
      <nav className="mtabs" aria-label="Main">
        {TABS.map((t) => (
          <Link key={t.href} href={t.href} className={active(path, t.href) ? "on" : ""} aria-current={active(path, t.href) ? "page" : undefined}>
            <span aria-hidden="true">{t.icon}</span><small>{t.label}</small>
          </Link>
        ))}
        <button type="button" className={more || inMore ? "on" : ""} aria-expanded={more} onClick={() => setMore((v) => !v)}>
          <span aria-hidden="true">⋯</span><small>More</small>
        </button>
      </nav>
    </>
  );
}
