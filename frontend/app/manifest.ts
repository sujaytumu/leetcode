import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "LeetCode Practice", short_name: "LeetCode", description: "Practice coding problems",
    orientation: "any", categories: ["education", "productivity"],
    start_url: "/", display: "standalone", background_color: "#1a1a1a", theme_color: "#1a1a1a",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
