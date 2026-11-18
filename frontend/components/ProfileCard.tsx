"use client";
import { useEffect, useState } from "react";
import { api, ProfileInfo } from "@/lib/api";
import { swr } from "@/lib/local";
import { AUTH_EVENT, authToken, authUser } from "@/lib/auth";
import Link from "next/link";

const EMPTY: ProfileInfo = {
  displayName: "", username: "", headline: "", company: "", location: "", school: "",
  website: "", github: "", linkedin: "", tags: [],
};

const initials = (i: ProfileInfo) =>
  (i.displayName || i.username || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");

interface Board { me: { rank: number; points: number; solved: number } | null; participants: number }

/** The header card of a LeetCode profile: photo, name, username, global rank, bio, links and skill tags. */
export default function ProfileCard() {
  const [info, setInfo] = useState<ProfileInfo | null>(null);
  const [rank, setRank] = useState<number | null>(null);
  const [photoOk, setPhotoOk] = useState(true);
  const [editing, setEditing] = useState(false);
  const [account, setAccount] = useState<string | null>(null);
  useEffect(() => {
    const sync = () => setAccount(authToken() ? authUser() : null);
    sync();
    window.addEventListener(AUTH_EVENT, sync);
    return () => window.removeEventListener(AUTH_EVENT, sync);
  }, []);

  useEffect(() => {
    swr<ProfileInfo>("/api/profile/info", (d) => setInfo(d), () => {}).catch(() => {});
    api<Board>("/api/leaderboard?limit=1").then((b) => setRank(b.me?.rank ?? null)).catch(() => {});
  }, []);

  const blank = info && !info.displayName && !info.username && !info.headline;
  return (
    <aside className="card profilecard">
      {!info && <div className="skel" style={{ width: "70%", height: 96 }} />}
      {info && (
        <>
          <div className="pc-top">
            {info.github && photoOk
              // eslint-disable-next-line @next/next/no-img-element
              ? <img className="avatar" src={`https://github.com/${info.github}.png?size=192`} alt="" onError={() => setPhotoOk(false)} />
              : <div className="avatar" aria-hidden="true">{initials(info)}</div>}
            <div className="pc-id">
              <div className="pc-name">{account ? (info.displayName || account) : "Anonymous coder"}</div>
              {account ? <div className="mute pc-user">{info.username || account}</div>
                : <div className="mute pc-user"><Link href="/login">Log in</Link> to see your name here</div>}
              <div className="pc-rank"><span className="mute">Rank</span> <b>{rank ? rank.toLocaleString("en-US") : "–"}</b></div>
            </div>
          </div>
          {info.headline && <p className="pc-headline">{info.headline}</p>}
          <button className="pc-edit" onClick={() => setEditing(true)}>{blank ? "Set up profile" : "Edit Profile"}</button>
          <ul className="pc-rows">
            {info.company && <li><span aria-hidden="true">🏢</span> {info.company}</li>}
            {info.location && <li><span aria-hidden="true">📍</span> {info.location}</li>}
            {info.school && <li><span aria-hidden="true">🎓</span> {info.school}</li>}
            {info.website && <li><span aria-hidden="true">🌐</span> <a href={info.website} target="_blank" rel="noopener noreferrer">{info.website.replace(/^https?:\/\//, "")}</a></li>}
            {info.github && <li><span aria-hidden="true">⌥</span> <a href={`https://github.com/${info.github}`} target="_blank" rel="noopener noreferrer">{info.github}</a></li>}
            {info.linkedin && <li><span aria-hidden="true">in</span> <a href={`https://www.linkedin.com/in/${info.linkedin}`} target="_blank" rel="noopener noreferrer">{info.linkedin}</a></li>}
          </ul>
          {info.tags.length > 0 && <div className="pc-tags">{info.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</div>}
        </>
      )}
      {editing && (
        <EditDialog initial={info ?? EMPTY} onClose={() => setEditing(false)} onSaved={(saved) => { setInfo(saved); setEditing(false); }} />
      )}
    </aside>
  );
}

function EditDialog({ initial, onClose, onSaved }:
  { initial: ProfileInfo; onClose: () => void; onSaved: (p: ProfileInfo) => void }) {
  const [f, setF] = useState({ ...initial, tags: initial.tags.join(", ") });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const set = (key: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [key]: e.target.value });

  async function save() {
    setSaving(true); setError("");
    try {
      const body = { ...f, tags: f.tags.split(",").map((t) => t.trim()).filter(Boolean) };
      onSaved(await api<ProfileInfo>("/api/profile/info", { method: "PUT", body: JSON.stringify(body) }));
    } catch (e) { setError(e instanceof Error ? e.message : "Could not save"); setSaving(false); }
  }

  const field = (label: string, key: keyof typeof f, placeholder = "", max = 60) => (
    <label className="pc-field"><span>{label}</span>
      <input value={f[key]} onChange={set(key)} placeholder={placeholder} maxLength={max} /></label>
  );
  return (
    <div className="modal-back" onClick={onClose}>
      <div className="modal pc-modal" role="dialog" aria-label="Edit profile" onClick={(e) => e.stopPropagation()}>
        <h3 style={{ marginTop: 0 }}>Edit profile</h3>
        {field("Name", "displayName", "Your name", 40)}
        {field("Username", "username", "letters, digits . _ -", 30)}
        {field("Headline", "headline", "e.g. SDE Intern | Full Stack Dev", 120)}
        {field("Company", "company")}
        {field("Location", "location")}
        {field("School", "school")}
        {field("Website", "website", "https://…", 120)}
        {field("GitHub username", "github")}
        {field("LinkedIn handle", "linkedin")}
        {field("Skills (comma separated, up to 8)", "tags", "java, springboot, dsa", 200)}
        {error && <div className="banner err">{error}</div>}
        <div className="bar" style={{ marginTop: 12 }}>
          <span className="grow" />
          <button onClick={onClose}>Cancel</button>
          <button className="primary" disabled={saving} onClick={save}>{saving ? "Saving…" : "Save"}</button>
        </div>
      </div>
    </div>
  );
}
