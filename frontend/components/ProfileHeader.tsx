"use client";
import { ReactNode, useState } from "react";
import { ProfileInfo } from "@/lib/api";

const initials = (i: ProfileInfo) =>
  (i.displayName || i.username || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join("");

/**
 * The header card of a LeetCode profile: photo, name, username, global rank, bio, follow counts, one action button
 * (Edit Profile on your own page, Follow on someone else's), links and skill tags.
 */
export default function ProfileHeader({ info, rank, social, action, footer }:
  { info: ProfileInfo; rank: number | null; social?: { followers: number; following: number }; action: ReactNode; footer?: ReactNode }) {
  const [photoOk, setPhotoOk] = useState(true);
  return (
    <aside className="card profilecard">
      <div className="pc-top">
        {info.github && photoOk
          // eslint-disable-next-line @next/next/no-img-element
          ? <img className="avatar" src={`https://github.com/${info.github}.png?size=192`} alt="" onError={() => setPhotoOk(false)} />
          : <div className="avatar" aria-hidden="true">{initials(info)}</div>}
        <div className="pc-id">
          <div className="pc-name">{info.displayName || "Anonymous coder"}</div>
          {info.username && <div className="mute pc-user">{info.username}</div>}
          <div className="pc-rank"><span className="mute">Rank</span> <b>{rank ? rank.toLocaleString("en-US") : "–"}</b></div>
        </div>
      </div>
      {info.headline && <p className="pc-headline">{info.headline}</p>}
      {social && (
        <div className="pc-social">
          <span><b>{social.following}</b> <span className="mute">Following</span></span>
          <span className="pc-sep" aria-hidden="true" />
          <span><b>{social.followers}</b> <span className="mute">Followers</span></span>
        </div>
      )}
      {action}
      <ul className="pc-rows">
        {info.company && <li><span aria-hidden="true">🏢</span> {info.company}</li>}
        {info.location && <li><span aria-hidden="true">📍</span> {info.location}</li>}
        {info.school && <li><span aria-hidden="true">🎓</span> {info.school}</li>}
        {info.website && <li><span aria-hidden="true">🌐</span> <a href={info.website} target="_blank" rel="noopener noreferrer">{info.website.replace(/^https?:\/\//, "")}</a></li>}
        {info.github && <li><span aria-hidden="true">⌥</span> <a href={`https://github.com/${info.github}`} target="_blank" rel="noopener noreferrer">{info.github}</a></li>}
        {info.linkedin && <li><span aria-hidden="true">in</span> <a href={`https://www.linkedin.com/in/${info.linkedin}`} target="_blank" rel="noopener noreferrer">{info.linkedin}</a></li>}
      </ul>
      {info.tags.length > 0 && <div className="pc-tags">{info.tags.map((t) => <span className="tag" key={t}>{t}</span>)}</div>}
      {footer}
    </aside>
  );
}
