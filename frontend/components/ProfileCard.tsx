"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import ProfileHeader from "@/components/ProfileHeader";
import { api, ProfileInfo } from "@/lib/api";
import { swr } from "@/lib/local";

const EMPTY: ProfileInfo = {
  displayName: "", username: "", headline: "", company: "", location: "", school: "",
  website: "", github: "", linkedin: "", tags: [],
};

interface Board { me: { rank: number; points: number; solved: number } | null; participants: number }

/** Your own header card: {@link ProfileHeader} with an Edit Profile button and a link to your public page. */
export default function ProfileCard({ social }: { social?: { followers: number; following: number } }) {
  const [info, setInfo] = useState<ProfileInfo | null>(null);
  const [rank, setRank] = useState<number | null>(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    swr<ProfileInfo>("/api/profile/info", (d) => setInfo(d), () => {}).catch(() => {});
    api<Board>("/api/leaderboard?limit=1").then((b) => setRank(b.me?.rank ?? null)).catch(() => {});
  }, []);

  if (!info) return <aside className="card profilecard"><div className="skel" style={{ width: "70%", height: 96 }} /></aside>;
  const blank = !info.displayName && !info.username && !info.headline;
  return (
    <>
      <ProfileHeader
        info={info}
        rank={rank}
        social={social}
        action={<button className="pc-edit" onClick={() => setEditing(true)}>{blank ? "Set up profile" : "Edit Profile"}</button>}
        footer={info.username
          ? <Link className="pc-public" href={`/u/${encodeURIComponent(info.username)}`}>View your public profile →</Link>
          : <p className="mute pc-public">Set a username to get a public profile page.</p>}
      />
      {editing && (
        <EditDialog initial={info} onClose={() => setEditing(false)} onSaved={(saved) => { setInfo(saved); setEditing(false); }} />
      )}
    </>
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
        <p className="mute" style={{ margin: "-4px 0 8px", fontSize: 12 }}>A username makes your profile public at /u/username. It must be unique.</p>
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
