"use client";
import { useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { position, trackPositions } from "@/lib/nav";

declare global { interface Window { __lcBack?: () => boolean } }


/**
 * Android app only (the native shell asks `window.__lcBack()` on the phone's Back button): go one screen back; from the
 * first screen go to the Problems tab; from there let the app go to the background. Overlays that use useBackClose
 * keep their own history entry, so Back closes them first.
 */
export default function BackHandler() {
  const path = usePathname() ?? "/";
  const router = useRouter();
  const pathRef = useRef(path);
  pathRef.current = path;

  useEffect(() => {
    trackPositions(); // every browser: the in-page Back buttons need to know whether an earlier screen exists
    if (!navigator.userAgent.includes("LeetcodeApp")) return;
    window.__lcBack = () => {
      if (position() > 0) { window.history.back(); return true; }
      if (pathRef.current !== "/problemset") { router.replace("/problemset"); return true; }
      return false;
    };
    return () => { delete window.__lcBack; };
  }, [router]);

  return null;
}
