"use client";
import { useRouter } from "next/navigation";
import { canGoBack } from "@/lib/nav";

/**
 * "Back" that returns to the page you actually came from. Only when this is the first screen of the visit (a shared
 * link, a reload) does it go to `fallback`. It stays a real link, so open-in-new-tab and copy-link still work.
 */
export default function BackLink({ fallback, children = "Back", className = "" }: { fallback: string; children?: React.ReactNode; className?: string }) {
  const router = useRouter();
  return (
    <a
      href={fallback}
      className={`backbtn ${className}`.trim()}
      onClick={(e) => {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        if (canGoBack()) router.back();
        else router.push(fallback);
      }}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6" /></svg>
      {children}
    </a>
  );
}
