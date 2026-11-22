"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ProfileInfo } from "@/lib/api";
import { authToken } from "@/lib/auth";
import type { ListSummary } from "@/lib/lists";
import { BIRTHDAY_KEY, GENDER_KEY, GENDERS, formatBirthday, readLocal, validBirthday, writeLocal } from "@/lib/localProfile";
import { FIELDS, FieldKey, normalizeField, valueOf } from "@/lib/settingsFields";
import { usePageTitle } from "@/lib/usePageTitle";
import { ICONS, SIDEBAR_ICONS } from "@/components/SettingsIcons";
import Skeleton from "@/components/Skeleton";

type Row = FieldKey | "gender" | "birthday" | "x";
const X_KEY = "lc-x";
const GENERAL: Row[] = ["displayName", "gender", "location", "birthday", "website", "github", "linkedin", "x", "headline", "username"];
const EXPERIENCE: Row[] = ["company", "school", "tags"];
const CURATE = [
  { key: "lc-show-ac", label: "Recent AC Problems and Submission Details", icon: "code" },
  { key: "lc-show-heatmap", label: "Submission Heatmap", icon: "heatmap" },
];
const LABEL: Record<Row, string> = {
  displayName: "Display Name", gender: "Gender", location: "Location", birthday: "Birthday", website: "Websites", github: "Github",
  linkedin: "LinkedIn", company: "Work", school: "Education", headline: "ReadMe", username: "Username", tags: "Skills", x: "X",
};
const SIDE = [
  { href: "/lists", label: "Library", icon: "library" }, { href: "/playground", label: "Project", icon: "project", beta: true },
  { href: "/daily", label: "Quest", icon: "quest" }, { href: "/topics", label: "Explore", icon: "explore" }, { href: "/plans", label: "Study Plan", icon: "plan" },
];
const initials = (i: ProfileInfo) => (i.displayName || i.username || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");

/** Settings > Profile, laid out like leetcode.com/settings/profile: sidebar with My Lists, avatar, then icon rows that open inline. */
export default function ProfileSettingsPage() {
  usePageTitle("Profile settings");
  const [info, setInfo] = useState<ProfileInfo | null>(null);
  const [lists, setLists] = useState<ListSummary[]>([]);
  const [error, setError] = useState("");
  const [open, setOpen] = useState<Row | null>(null);
  const [draft, setDraft] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState<Row | null>(null);
  const [photoOk, setPhotoOk] = useState(true);
  const [gender, setGender] = useState("");
  const [birthday, setBirthday] = useState("");
  const [xHandle, setXHandle] = useState("");
  const [flags, setFlags] = useState<Record<string, boolean>>({});
  const signedIn = typeof window !== "undefined" && !!authToken();

  useEffect(() => {
    setGender(readLocal(GENDER_KEY)); setBirthday(readLocal(BIRTHDAY_KEY)); setXHandle(readLocal(X_KEY));
    setFlags(Object.fromEntries(CURATE.map((c) => [c.key, readLocal(c.key) !== "off"])));
    api<ProfileInfo>("/api/profile/info").then(setInfo).catch((e: Error) => setError(e.message));
    api<ListSummary[]>("/api/lists").then(setLists).catch(() => setLists([]));
  }, []);

  const current = (r: Row): string => r === "gender" ? gender : r === "birthday" ? birthday : r === "x" ? xHandle : info ? valueOf(info, r) : "";
  const shown = (r: Row): string => r === "birthday" ? formatBirthday(birthday) : current(r);

  function edit(r: Row) {
    setOpen(open === r ? null : r); setDraft(current(r)); setFieldError(""); setSaved(null);
  }

  async function save(r: Row) {
    if (!info || busy) return;
    if (r === "x") { writeLocal(X_KEY, draft.trim()); setXHandle(draft.trim()); setOpen(null); setSaved(r); return; }
    if (r === "gender") { writeLocal(GENDER_KEY, draft); setGender(draft); setOpen(null); setSaved(r); return; }
    if (r === "birthday") {
      if (draft && !validBirthday(draft)) { setFieldError("Pick a real date in the past."); return; }
      writeLocal(BIRTHDAY_KEY, draft); setBirthday(draft); setOpen(null); setSaved(r); return;
    }
    const { value, error: err } = normalizeField(r, draft);
    if (err) { setFieldError(err); return; }
    setBusy(true); setFieldError("");
    try {
      const next = await api<ProfileInfo>("/api/profile/info", { method: "PUT", body: JSON.stringify({ ...info, [r]: r === "tags" ? value.split(",").map((t) => t.trim()).filter(Boolean) : value }) });
      setInfo(next); setOpen(null); setSaved(r); setPhotoOk(true);
    } catch (e) { setFieldError((e as Error).message); }
    setBusy(false);
  }

  if (error) return <div className="banner err">{error}</div>;
  if (!info) return <Skeleton lines={8} />;
  const field = FIELDS.find((f) => f.key === open);
  const renderRows = (list: Row[]) => (
    <div className="lcrows">
          {list.map((r) => (
            <div key={r} className={`lcrow${open === r ? " open" : ""}`}>
              <button type="button" className="lcrowhead" onClick={() => edit(r)} aria-expanded={open === r}>
                <span className="lcrowicon">{ICONS[r === "birthday" ? "birthday" : r === "gender" ? "gender" : r]}</span>
                <b>{LABEL[r]}</b>
                {r === "tags"
                  ? <span className="lcrowval lcchips">{info.tags.map((t) => <em key={t}>{t}</em>)}</span>
                  : <span className="lcrowval">{shown(r) || ""}</span>}
                {saved === r && <span className="setsaved">Saved</span>}
                <span className="lcarrow" aria-hidden="true">→</span>
              </button>
              {open === r && (
                <form className="setedit" onSubmit={(e) => { e.preventDefault(); void save(r); }}>
                  {r === "gender" ? (
                    <select value={draft} onChange={(e) => setDraft(e.target.value)} aria-label="Gender">
                      <option value="">Not set</option>
                      {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
                    </select>
                  ) : r === "birthday" ? (
                    <input type="date" value={draft} onChange={(e) => setDraft(e.target.value)} aria-label="Birthday" />
                  ) : (
                    <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder={field?.placeholder} maxLength={(field?.max ?? 100) + 40}
                      autoFocus autoCapitalize="none" spellCheck={false} aria-label={LABEL[r]} />
                  )}
                  {(r === "gender" || r === "birthday") && <span className="mute" style={{ fontSize: 12 }}>Stays on this device. It is never sent to the server.</span>}
                  {field?.hint && <span className="mute" style={{ fontSize: 12 }}>{field.hint}</span>}
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
  );
  return (
    <div className="lcset">
      <aside className="lcsetside">
        <nav aria-label="Library">
          {SIDE.map((s) => (
            <Link key={s.href} href={s.href} className="lcsetlink">{SIDEBAR_ICONS[s.icon]}<span>{s.label}</span>{s.beta && <em className="lcbeta">Beta</em>}</Link>
          ))}
        </nav>
        <div className="lcsetlists">
          <div className="lcsetlistshead"><span>My Lists</span><Link href="/lists" aria-label="Create or manage lists">＋ ⌄</Link></div>
          <Link href="/lists" className="lcsetlist">{SIDEBAR_ICONS.star}<span>Favorite</span><i>{SIDEBAR_ICONS.lock}</i></Link>
          {lists.filter((l) => l.name.toLowerCase() !== "favorite").map((l) => (
            <Link key={l.id} href="/lists" className="lcsetlist">{SIDEBAR_ICONS.list}<span>{l.name}</span><i>{SIDEBAR_ICONS.lock}</i></Link>
          ))}
        </div>
      </aside>
      <section className="lcsetmain">
        <div className="lcavatar">
          {info.github && photoOk
            // eslint-disable-next-line @next/next/no-img-element
            ? <img src={`https://github.com/${info.github}.png?size=240`} alt="" onError={() => setPhotoOk(false)} />
            : <div aria-hidden="true">{initials(info)}</div>}
        </div>
        <p className="mute lcavatarnote">Your photo comes from your GitHub username.</p>
        {!signedIn && <div className="banner" style={{ marginBottom: 12 }}>You are not logged in, so these details stay on this device only. <Link href="/login">Log in</Link></div>}
        <h3 className="lcgeneral">General</h3>
        <p className="mute lcgeneralsub">Manage your basic profile information.</p>
        {renderRows(GENERAL)}
        <h3 className="lcgeneral lcsec">Experience</h3>
        <p className="mute lcgeneralsub">Share your growth from learning to career.</p>
        {renderRows(EXPERIENCE)}
        <h3 className="lcgeneral lcsec">Curate your profile</h3>
        <p className="mute lcgeneralsub">Control what opens to the public. Saved on this device.</p>
        <div className="lcrows">
          {CURATE.map((c) => (
            <div key={c.key} className="lcrow">
              <div className="lcrowhead lctoggle">
                <span className="lcrowicon">{ICONS[c.icon]}</span>
                <b>{c.label}</b>
                <span className="lcrowval" />
                <button type="button" role="switch" aria-checked={flags[c.key] !== false} aria-label={c.label}
                  className={`lcswitch${flags[c.key] !== false ? " on" : ""}`}
                  onClick={() => { const v = flags[c.key] === false; writeLocal(c.key, v ? "on" : "off"); setFlags({ ...flags, [c.key]: v }); }}>
                  <i />
                </button>
                <span className="lcswitchlabel">{flags[c.key] !== false ? "On" : "Off"}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
