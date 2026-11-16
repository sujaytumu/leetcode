import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "LeetCode Practice", description: "Practice coding problems" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="nav"><Link href="/" className="brand">&lt;/&gt; LeetCode Practice</Link></header>
        <main>{children}</main>
      </body>
    </html>
  );
}
