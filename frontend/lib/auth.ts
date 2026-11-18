/** Browser-side session for accounts. The backend still keys all data by client id; an account just owns one. */
const TOKEN = "lc-auth-token";
const USER = "lc-auth-user";
const CLIENT = "lc-client-id";
export const AUTH_EVENT = "lc-auth";

export interface Session { token: string; clientId: string; username: string }

function get(key: string): string | null {
  try { return localStorage.getItem(key); } catch { return null; }
}

export function authToken(): string | null { return get(TOKEN); }
export function authUser(): string | null { return get(USER); }

export function authHeaders(): Record<string, string> {
  const t = authToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

function clearCaches() {
  try { Object.keys(localStorage).filter((k) => k.startsWith("lc-cache:")).forEach((k) => localStorage.removeItem(k)); } catch {}
}

function announce() { window.dispatchEvent(new Event(AUTH_EVENT)); }

/** After register/login: adopt the account's client id so every request and cache lines up with it. */
export function setSession(s: Session) {
  localStorage.setItem(TOKEN, s.token);
  localStorage.setItem(USER, s.username);
  localStorage.setItem(CLIENT, s.clientId);
  clearCaches();
  announce();
}

/** Explicit log out: this browser becomes a fresh anonymous user so the next person on it does not inherit the account. */
export function clearSession() {
  try {
    localStorage.removeItem(TOKEN);
    localStorage.removeItem(USER);
    localStorage.setItem(CLIENT, crypto.randomUUID());
  } catch {}
  clearCaches();
  announce();
}

/** The token was rejected (expired or revoked): keep the id so logging in again lands on the same data. */
export function expireSession() {
  try { localStorage.removeItem(TOKEN); } catch {}
  announce();
}
