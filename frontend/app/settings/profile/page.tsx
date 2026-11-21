"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ProfileInfo } from "@/lib/api";
import { authToken } from "@/lib/auth";
import { FIELDS, FieldKey, normalizeField, valueOf } from "@/lib/settingsFields";
import { usePageTitle } from "@/lib/usePageTitle";
import Skeleton from "@/components/Skeleton";

const initials = (i: ProfileInfo) => (i.displayName || i.username || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");

/** Settings > Profile, laid out like leetcode.com/settings/profile: avatar on top, then one row per field that opens inline. */
export default function ProfileSettingsPage() {
  usePageTitle("Profile settings");
  const [info, setInfo] = useState<ProfileInfo | null>(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState<FieldKey | null>(null);
  const [draft, setDraft] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState<FieldKey | null>(null);
  const [photoOk, setPhotoOk] = useState(true);
  const signedIn = typeof window !== "undefined" && !!authToken();

  useEffect(() => { api<ProfileInfo>("/api/profile/info").then(setInfo).catch((e: Error) => setError(e.message)); }, []);

  function edit(key: FieldKey) {
    if (!info) return;
    setOpen(open === key ? null : key); setDraft(valueOf(info, key)); setFieldError(""); setSaved(null);
  }

  async function save(key: FieldKey) {
    if (!info || busy) return;
    const { value, error: err } = normalizeField(key, draft);
    if (err) { setFieldError(err); return; }
    setBusy(true); setFieldError("");
    try {
      const next = await api<ProfileInfo>("/api/profile/info", { method: "PUT", body: JSON.stringify({ ...info, [key]: value }) });
      setInfo(next); setOpen(null); setSaved(key); setPhotoOk(true);
    } catch (e) { setFieldError((e as Error).message); }
    setBusy(false);
  }

  if (error) return <div className="banner err">{error}</div>;
  if (!info) return <Skeleton lines={8} />;
  return (
    <div className="settings">
      <nav className="settingsnav" aria-label="Settings">
        <Link href="/settings/profile" className="on">Profile</Link>
        <Link href="/account">Account</Link>
        <Link href="/profile">Public profile</Link>
      </nav>
      <section className="settingsmain">
        <div className="setavatar">
          {info.github && photoOk
            // eslint-disable-next-line @next/next/no-img-element
            ? <img src={`https://github.com/${info.github}.png?size=240`} alt="" onError={() => setPhotoOk(false)} />
            : <div aria-hidden="true">{initials(info)}</div>}
        </div>
        <p className="mute" style={{ textAlign: "center", margin: "6px 0 22px", fontSize: 13 }}>
          Your avatar comes from your GitHub username. Set it below.
        </p>
        {!signedIn && <div className="banner" style={{ marginBottom: 12 }}>You are not logged in, so these details stay on this device only. <Link href="/login">Log in</Link></div>}
        <h3 style={{ margin: "0 0 2px" }}>General</h3>
        <p className="mute" style={{ margin: "0 0 10px", fontSize: 13 }}>Manage your basic profile information.</p>
        <div className="setlist">
          {FIELDS.map((f) => (
            <div key={f.key} className={`setrow${open === f.key ? " open" : ""}`}>
              <button type="button" className="setrowhead" onClick={() => edit(f.key)} aria-expanded={open === f.key}>
                <b>{f.label}</b>
                <span className="mute setval">{valueOf(info, f.key) || "Not set"}</span>
                {saved === f.key && <span className="setsaved">Saved</span>}
                <span className="setarrow" aria-hidden="true">{open === f.key ? "⌄" : "›"}</span>
              </button>
              {open === f.key && (
                <form className="setedit" onSubmit={(e) => { e.preventDefault(); void save(f.key); }}>
                  <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder={f.placeholder} maxLength={f.max + 40} autoFocus
                    autoCapitalize="none" spellCheck={false} aria-label={f.label} />
                  {f.hint && <span className="mute" style={{ fontSize: 12 }}>{f.hint}</span>}
                  {fieldError && <div className="banner err" role="alert">{fieldError}</div>}
                  <div className="bar">
                    <button className="primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
                    <button type="button" onClick={() => setOpen(null)}>Cancel</button>
                  </div>
                </form>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
