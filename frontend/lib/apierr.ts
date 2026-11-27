/** Small pure helpers for API failures (kept import-free so they are easy to unit-test). */

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** The server requires X-Client-Id to be a UUID; anything else is answered with HTTP 400 on every call. */
export const isClientId = (v: string | null | undefined): v is string => !!v && UUID.test(v);

/** The text shown for a failed request. A 400 names the endpoint so a rejected request can be traced at a glance. */
export function failureMessage(status: number, detail: string, path: string): string {
  const transient = status === 502 || status === 503 || status === 504;
  if (!detail) detail = transient ? "The server is starting up." : status === 400 ? "The server rejected the request." : `Request failed (HTTP ${status}).`;
  if (status === 400) return `${detail.replace(/\.$/, "")} (HTTP 400 on ${path.split("?")[0]})`;
  return detail;
}
