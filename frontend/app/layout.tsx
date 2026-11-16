import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "LeetCode Practice", description: "Practice coding problems",
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
  appleWebApp: { capable: true, title: "LeetCode", statusBarStyle: "black-translucent" },
};
export const viewport: Viewport = { themeColor: "#0f1115", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="nav">
          <Link href="/" className="brand">&lt;/&gt; LeetCode Practice</Link>
          <nav><Link href="/">Problems</Link><Link href="/plans">Plans</Link></nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
