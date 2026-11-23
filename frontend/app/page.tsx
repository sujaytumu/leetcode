"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ProfilePage from "./profile/page";
import Skeleton from "@/components/Skeleton";
import { api, ProfileInfo } from "@/lib/api";

/** The main page is your profile at /<username>, like LeetCode. Without a username yet it shows your profile here. */
export default function Home() {
  const router = useRouter();
  const [state, setState] = useState<"checking" | "here">("checking");
  useEffect(() => {
    api<ProfileInfo>("/api/profile/info")
      .then((i) => { if (i.username) router.replace(`/${encodeURIComponent(i.username)}`); else setState("here"); })
      .catch(() => setState("here"));
  }, [router]);
  return state === "here" ? <ProfilePage /> : <Skeleton lines={10} />;
}
