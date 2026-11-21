import type { ProfileInfo } from "./api";

export type FieldKey = "displayName" | "username" | "headline" | "location" | "company" | "school" | "website" | "github" | "linkedin";
export interface Field { key: FieldKey; label: string; placeholder: string; max: number; hint?: string }

/** The rows of LeetCode's Settings > Profile > General list, mapped onto the fields this app stores. */
export const FIELDS: Field[] = [
  { key: "displayName", label: "Display Name", placeholder: "Your name", max: 60 },
  { key: "username", label: "Username", placeholder: "letters, digits, _ or -", max: 30, hint: "Your profile lives at /username." },
  { key: "headline", label: "Summary", placeholder: "A short line about you", max: 200 },
  { key: "location", label: "Location", placeholder: "City, Country", max: 80 },
  { key: "company", label: "Company", placeholder: "Where you work", max: 80 },
  { key: "school", label: "School", placeholder: "Where you study", max: 80 },
  { key: "website", label: "Website", placeholder: "https://example.com", max: 200 },
  { key: "github", label: "GitHub", placeholder: "username or github.com/username", max: 100, hint: "Your GitHub photo is used as your avatar." },
  { key: "linkedin", label: "LinkedIn", placeholder: "linkedin.com/in/you", max: 100 },
];

/** Accepts `sujaytumu`, `@sujaytumu` or a full github.com URL and returns just the username ("" when empty). */
export function cleanGithub(raw: string): string | null {
  let v = raw.trim().replace(/^@/, "");
  const m = v.match(/^(?:https?:\/\/)?(?:www\.)?github\.com\/([^/?#\s]+)/i);
  if (m) v = m[1];
  if (v === "") return "";
  return /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/.test(v) ? v : null;
}

/** Adds https:// when missing; returns null for something that cannot be a web address. */
export function cleanWebsite(raw: string): string | null {
  const v = raw.trim();
  if (v === "") return "";
  const url = /^https?:\/\//i.test(v) ? v : `https://${v}`;
  try {
    const u = new URL(url);
    return u.hostname.includes(".") ? url : null;
  } catch { return null; }
}

export function cleanUsername(raw: string): string | null {
  const v = raw.trim();
  return /^[A-Za-z0-9_-]{3,30}$/.test(v) ? v : null;
}

/** Validates and normalises one field; `error` is set when the value is not acceptable. */
export function normalizeField(key: FieldKey, raw: string): { value: string; error?: string } {
  const f = FIELDS.find((x) => x.key === key)!;
  const v = raw.trim();
  if (v.length > f.max) return { value: v, error: `At most ${f.max} characters.` };
  if (key === "github") { const g = cleanGithub(v); return g === null ? { value: v, error: "That is not a valid GitHub username." } : { value: g }; }
  if (key === "website") { const w = cleanWebsite(v); return w === null ? { value: v, error: "Enter a full web address, like https://example.com." } : { value: w }; }
  if (key === "username") { const u = cleanUsername(v); return u === null ? { value: v, error: "3-30 letters, digits, _ or -." } : { value: u }; }
  if (key === "displayName" && v === "") return { value: v, error: "Display name cannot be empty." };
  return { value: v };
}

export const valueOf = (info: ProfileInfo, key: FieldKey): string => (info[key] as string) ?? "";
