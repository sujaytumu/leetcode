"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [{ href: "/problemset", label: "Problems" }, { href: "/contest", label: "Contest" }, { href: "/leaderboard", label: "Ranking" }, { href: "/playground", label: "Playground" }];

export default function NavLinks() {
  const path = usePathname();
  return (
    <>
      {LINKS.map((l) => {
        const on = l.href === "/problemset" ? path.startsWith("/problemset") || path.startsWith("/problems") : path.startsWith(l.href);
        return <Link key={l.href} href={l.href} className={on ? "active" : ""}>{l.label}</Link>;
      })}
    </>
  );
}
