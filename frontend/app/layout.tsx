import "./globals.css";
import type { Metadata, Viewport } from "next";
import NavBar from "@/components/NavBar";
import WakeUp from "@/components/WakeUp";

export const metadata: Metadata = {
  title: "LeetCode Practice", description: "Practice coding problems",
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
  appleWebApp: { capable: true, title: "LeetCode", statusBarStyle: "black-translucent" },
};
export const viewport: Viewport = { themeColor: "#282828", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WakeUp />
        <NavBar />
        {children}
      </body>
    </html>
  );
}
