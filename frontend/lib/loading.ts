/** Tiny store counting in-flight GET requests so the UI can show a single "Loading…" indicator. */
let count = 0;
const listeners = new Set<() => void>();
const emit = () => listeners.forEach((l) => l());

export const loading = {
  start() { count++; emit(); },
  end() { count = Math.max(0, count - 1); emit(); },
  active: () => count > 0,
  subscribe(fn: () => void) { listeners.add(fn); return () => { listeners.delete(fn); }; },
};
