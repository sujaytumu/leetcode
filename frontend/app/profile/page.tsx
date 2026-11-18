"use client";
import BackupCard from "@/components/BackupCard";
import WeeklySummary from "@/components/WeeklySummary";
import ExportCard from "@/components/ExportCard";
import SyncCard from "@/components/SyncCard";
import { useEffect, useState } from "react";
import ProfileCard from "@/components/ProfileCard";
import ProfileLayout from "@/components/ProfileLayout";
import { Profile, profilePath } from "@/lib/api";
import Skeleton from "@/components/Skeleton";
import { swr } from "@/lib/local";

export default function ProfilePage() {
  const [p, setP] = useState<Profile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    swr<Profile>(profilePath(), (d) => setP(d), () => {}).catch((e) => setError(e.message));
  }, []);

  if (!p) {
    return (
      <>
        {error && <div className="banner err">{error}</div>}
        {!error && <Skeleton lines={10} />}
      </>
    );
  }

  return (
    <ProfileLayout
      p={p}
      header={<ProfileCard social={p.social} />}
      extras={<div className="stack"><WeeklySummary calendar={p.calendar} /><SyncCard /><ExportCard /><BackupCard /></div>}
    />
  );
}
