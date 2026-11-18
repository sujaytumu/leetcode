"use client";
import { useEffect } from "react";

/** Sets the browser tab title for a client page, e.g. "Review queue · LeetCode Practice". */
export function usePageTitle(title: string) {
  useEffect(() => { document.title = `${title} · LeetCode Practice`; }, [title]);
}
