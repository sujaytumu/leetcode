"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [{ href: "/", label: "Problems" }, { href: "/topics", label: "Topics" }, { href: "/for-you", label: "For you" }, { href: "/plans", label: "Plans" }, { href: "/review", label: "Review" }, { href: "/lists", label: "Lists" }, { href: "/mock", label: "Mock" }, { href: "/contest", label: "Contest" }, { href: "/leaderboard", label: "Ranking" }, { href: "/playground", label: "Playground" }];

export default function NavLinks() {
  const path = usePathname();
  return (
    <>
      {LINKS.map((l) => {
        const on = l.href === "/" ? path === "/" || path.startsWith("/problems") : path.startsWith(l.href);
        return <Link key={l.href} href={l.href} className={on ? "active" : ""}>{l.label}</Link>;
      })}
    </>
  );
}
