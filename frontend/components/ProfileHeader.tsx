"use client";
import { uploadedPhoto } from "@/lib/photo";
import { ReactNode, useState } from "react";
import { ProfileInfo } from "@/lib/api";

const Svg = ({ children }: { children: ReactNode }) => (
  <svg className="pc-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
);
const ICON = {
  company: <Svg><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3 13h18" /></Svg>,
  location: <Svg><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z" /><circle cx="12" cy="9.5" r="2.5" /></Svg>,
  school: <Svg><path d="M2 9l10-5 10 5-10 5L2 9z" /><path d="M6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5" /></Svg>,
  website: <Svg><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9S14.5 18.3 12 21c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z" /></Svg>,
  github: <Svg><path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21" /></Svg>,
  linkedin: <Svg><rect x="3" y="3" width="18" height="18" rx="3" /><path d="M8 10.5V16M8 7.8v.1M12 16v-5.5M12 13c0-1.7 1-2.6 2.3-2.6S16.5 11.3 16.5 13V16" /></Svg>,
  tags: <Svg><path d="M12.6 3H5a2 2 0 0 0-2 2v7.6a2 2 0 0 0 .6 1.4l7 7a2 2 0 0 0 2.8 0l6.2-6.2a2 2 0 0 0 0-2.8l-7-7A2 2 0 0 0 12.6 3z" /><circle cx="8" cy="8" r="1.300" /></Svg>,
};

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
        {uploadedPhoto(info)
          // eslint-disable-next-line @next/next/no-img-element
          ? <img className="avatar" src={uploadedPhoto(info)!} alt="" />
          : info.github && photoOk
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
        {info.company && <li>{ICON.company} {info.company}</li>}
        {info.location && <li>{ICON.location} {info.location}</li>}
        {info.school && <li>{ICON.school} {info.school}</li>}
        {info.website && <li>{ICON.website} <a href={info.website} target="_blank" rel="noopener noreferrer">{info.website.replace(/^https?:\/\//, "")}</a></li>}
        {info.github && <li>{ICON.github} <a href={`https://github.com/${info.github}`} target="_blank" rel="noopener noreferrer">{info.github}</a></li>}
        {info.linkedin && <li>{ICON.linkedin} <a href={`https://www.linkedin.com/in/${info.linkedin}`} target="_blank" rel="noopener noreferrer">{info.linkedin}</a></li>}
      </ul>
      {info.tags.length > 0 && <div className="pc-tags">{ICON.tags}<div className="pc-tagwrap">{info.tags.map((t) => <span className="pc-pill" key={t}>{t}</span>)}</div></div>}
      {footer}
    </aside>
  );
}
