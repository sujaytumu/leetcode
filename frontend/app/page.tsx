"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import ProfilePage from "./profile/page";
import { api, ProfileInfo } from "@/lib/api";

/** The main page is your profile at /<username>, like LeetCode. Without a username yet it shows your profile here. */
export default function Home() {
  const router = useRouter();
  // Your profile shows at once (from the saved copy); the address moves to /<username> when the server answers.
  useEffect(() => {
    let here = true;
    api<ProfileInfo>("/api/profile/info")
      .then((i) => { if (here && i.username) router.replace(`/${encodeURIComponent(i.username)}`); })
      .catch(() => { /* stay here */ });
    return () => { here = false; };
  }, [router]);
  return <ProfilePage />;
}
