"use client";
import { useEffect, useState } from "react";
import { Meta } from "./api";
import { swr } from "./local";

let latest: Meta | null = null;

/** Languages, difficulty/status options and paging defaults, owned by the backend (GET /api/meta). */
export function useMeta(): Meta | null {
  const [meta, setMeta] = useState<Meta | null>(latest);
  useEffect(() => {
    swr<Meta>("/api/meta", (m) => { latest = m; setMeta(m); }, () => {}).catch(() => {});
  }, []);
  return meta;
}
