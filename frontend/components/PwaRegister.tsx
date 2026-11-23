"use client";
import { useEffect, useState } from "react";

type InstallPrompt = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> };
const DISMISSED = "lc-install-dismissed";

/** Registers the offline service worker, offers "Install app" when the browser allows it, and shows an offline notice. */
export default function PwaRegister() {
  const [prompt, setPrompt] = useState<InstallPrompt | null>(null);
  const [online, setOnline] = useState(true);

  useEffect(() => {
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker.register("/sw.js").catch(() => { /* offline support is optional */ });
    }
    setOnline(navigator.onLine);
    const up = () => setOnline(true), down = () => setOnline(false);
    const onPrompt = (e: Event) => {
      e.preventDefault();
      let dismissed = false;
      try { dismissed = !!localStorage.getItem(DISMISSED); } catch { /* storage blocked */ }
      if (!dismissed) setPrompt(e as InstallPrompt);
    };
    const onInstalled = () => setPrompt(null);
    window.addEventListener("online", up);
    window.addEventListener("offline", down);
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("online", up);
      window.removeEventListener("offline", down);
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  const dismiss = () => {
    try { localStorage.setItem(DISMISSED, "1"); } catch { /* storage blocked */ }
    setPrompt(null);
  };
  const install = async () => {
    if (!prompt) return;
    await prompt.prompt();
    await prompt.userChoice.catch(() => undefined);
    setPrompt(null);
  };

  return (
    <>
      {!online && <div className="offline-bar" role="status">You're offline. Saved pages and the problem list still work; running code needs a connection.</div>}
      {prompt && (
        <div className="install-toast" role="dialog" aria-label="Install the app">
          <span>Install this as an app for faster launch and offline access.</span>
          <button className="primary" onClick={install}>Install</button>
          <button onClick={dismiss} aria-label="Not now">Not now</button>
        </div>
      )}
    </>
  );
}
