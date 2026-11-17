"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [{ href: "/", label: "Problems" }, { href: "/plans", label: "Plans" }, { href: "/profile", label: "Profile" }];

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
