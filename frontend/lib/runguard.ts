/** Languages the judge accepts (mirrors backend Language enum). Lets the editor choose one before /api/meta arrives. */
export const JUDGE_LANGS = ["cpp", "java", "python", "javascript"] as const;
/** Backend limit on submitted source (RunRequest.code @Size). */
export const MAX_SOURCE_CHARS = 65536;

export const isJudgeLang = (k: string | null | undefined): k is string => !!k && (JUDGE_LANGS as readonly string[]).includes(k);

/** The language to open with: ?lang= link, then the saved choice, then C++. Never empty, so Run/Submit never send a blank language. */
export function initialLang(asked: string | null, saved: string | null): string {
  return isJudgeLang(asked) ? asked : isJudgeLang(saved) ? saved : "cpp";
}

/** A message to show instead of calling the server when the request would be rejected with HTTP 400; null when it can be sent. */
export function runBlocker(lang: string, source: string): string | null {
  if (!isJudgeLang(lang)) return "Pick a language first, then run again.";
  if (!source.trim()) return "The editor is empty. Write your solution (or reset to the starter code), then run again.";
  if (source.length > MAX_SOURCE_CHARS) return `Your code is too long (${source.length.toLocaleString()} characters; the limit is ${MAX_SOURCE_CHARS.toLocaleString()}).`;
  return null;
}
