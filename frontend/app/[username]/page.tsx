"use client";
import BackLink from "@/components/BackLink";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import ProfileHeader from "@/components/ProfileHeader";
import OwnProfile from "@/app/profile/page";
import ProfileLayout from "@/components/ProfileLayout";
import Skeleton from "@/components/Skeleton";
import { api, PublicProfile, publicProfilePath } from "@/lib/api";
import { swr } from "@/lib/local";

/** Someone's public profile, addressed by the username they chose. Same layout as your own, read-only, with Follow. */
export default function PublicProfilePage() {
  const { username } = useParams<{ username: string }>();
  const name = decodeURIComponent(username);
  const [data, setData] = useState<PublicProfile | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    // Saved copy first, then the live one (retrying while the server wakes).
    swr<PublicProfile>(publicProfilePath(name), (d) => { setData(d); setError(""); }, () => {}).catch((e: Error) => setError(e.message));
  }, [name]);
  useEffect(() => { setData(null); load(); }, [load]);

  async function toggleFollow() {
    if (!data || busy) return;
    setBusy(true);
    try {
      await api(`/api/users/${encodeURIComponent(name)}/follow`, { method: data.youFollow ? "DELETE" : "PUT" });
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  if (error && !data) {
    return (
      <section className="card authcard">
        <h3 style={{ marginTop: 0 }}>Profile not found</h3>
        <p className="mute">{error}</p>
        <BackLink fallback="/leaderboard" />
      </section>
    );
  }
  if (!data) return <Skeleton lines={10} />;
  if (data.you) return <OwnProfile />;

  const action = data.you
    ? <Link className="pc-edit pc-link" href="/profile">Edit Profile</Link>
    : <button className={data.youFollow ? "pc-edit pc-following" : "pc-edit"} disabled={busy} onClick={toggleFollow}>
        {data.youFollow ? "Following" : "+ Follow"}
      </button>;
  return (
    <>
      {error && <div className="banner err">{error}</div>}
      <ProfileLayout
        p={data.profile}
        own={data.you}
        ratingPath={`/api/users/${encodeURIComponent(name)}/rating`}
        header={<ProfileHeader info={data.info} rank={data.rank} social={data.profile.social} action={action} />}
      />
    </>
  );
}
