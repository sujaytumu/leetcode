"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    swr<ProfileInfo>("/api/profile/info", (d) => setInfo(d), () => {}).catch(() => {});
    api<Board>("/api/leaderboard?limit=1").then((b) => setRank(b.me?.rank ?? null)).catch(() => {});
  }, []);

  if (!info) return <aside className="card profilecard"><div className="skel" style={{ width: "70%", height: 96 }} /></aside>;
  const share = async () => {
    if (!info.username) { router.push("/settings/profile"); return; }
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/${encodeURIComponent(info.username)}`);
      setCopied(true); setTimeout(() => setCopied(false), 1800);
    } catch { /* clipboard blocked */ }
  };
  const blank = !info.displayName && !info.username && !info.headline;
  return (
    <>
      <ProfileHeader
        info={info}
        rank={rank}
        social={social}
        action={
          <div className="pc-actions">
            <button className="pc-edit" onClick={() => router.push("/settings/profile")}>{blank ? "Set up profile" : "Edit Profile"}</button>
            <button type="button" className="pc-share" onClick={share} aria-label="Copy public profile link" title={info.username ? (copied ? "Link copied" : "Copy public profile link") : "Set a username to share"}>
              {copied
                ? <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
                : <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 15V4M8 8l4-4 4 4M5 13v6a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-6" /></svg>}
            </button>
          </div>}
        footer={info.username
          ? <Link className="pc-public" href={`/${encodeURIComponent(info.username)}`}>View your public profile →</Link>
          : <p className="mute pc-public">Set a username to get a public profile page.</p>}
      />
    </>
  );
}
