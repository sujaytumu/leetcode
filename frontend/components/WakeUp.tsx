"use client";
import { useEffect } from "react";
import { pingServer } from "@/lib/catalog";

/** Starts waking the free-tier backend as soon as any page opens, so it is ready by the time Run/Submit is used. */
export default function WakeUp() {
  useEffect(() => { pingServer(); }, []);
  return null;
}
