/** Personal details that only ever live on this device (the server has no field for them). */
export const GENDER_KEY = "lc-gender";
export const BIRTHDAY_KEY = "lc-birthday";
export const GENDERS = ["Male", "Female", "Other", "Prefer not to say"] as const;

export function readLocal(key: string, storage: Pick<Storage, "getItem"> = localStorage): string {
  try { return storage.getItem(key) ?? ""; } catch { return ""; }
}
export function writeLocal(key: string, value: string, storage: Pick<Storage, "setItem" | "removeItem"> = localStorage): void {
  try { if (value) storage.setItem(key, value); else storage.removeItem(key); } catch { /* storage blocked */ }
}

/** "2004-12-14" -> "December 14, 2004"; anything unreadable gives "". */
export function formatBirthday(iso: string): string {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return "";
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  if (d.getFullYear() !== Number(m[1]) || d.getMonth() !== Number(m[2]) - 1 || d.getDate() !== Number(m[3])) return "";
  return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
}

/** Valid, not in the future, not absurdly old. */
export function validBirthday(iso: string, now: Date = new Date()): boolean {
  if (!formatBirthday(iso)) return false;
  const d = new Date(`${iso}T00:00:00`);
  return d <= now && d.getFullYear() >= 1900;
}
