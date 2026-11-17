import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";
import ThemeToggle from "@/components/ThemeToggle";
import LoadingIndicator from "@/components/LoadingIndicator";
import NavLinks from "@/components/NavLinks";
import MockBar from "@/components/MockBar";
import CommandPalette, { PaletteButton } from "@/components/CommandPalette";

export const metadata: Metadata = {
  title: "LeetCode Practice", description: "Practice coding problems",
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
  appleWebApp: { capable: true, title: "LeetCode", statusBarStyle: "black-translucent" },
};
export const viewport: Viewport = { themeColor: "#0f1115", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Apply the saved theme before first paint so there is no flash of the wrong theme. */}
        <script dangerouslySetInnerHTML={{ __html:
          "try{if(localStorage.getItem('lc-theme')==='light')document.documentElement.dataset.theme='light'}catch(e){}" +
          // Start waking the (free-tier) backend the moment the page arrives, before any app code runs.
          `try{fetch(${JSON.stringify((process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080") + "/actuator/health")},{mode:'no-cors',keepalive:true})}catch(e){}` }} />
      </head>
      <body>
        <header className="nav">
          <Link href="/" className="brand">&lt;/&gt;<span className="brand-text"> LeetCode Practice</span></Link>
          <nav><LoadingIndicator /><NavLinks /><PaletteButton /><ThemeToggle /></nav>
        </header>
        <MockBar />
        <main>{children}</main>
        <CommandPalette />
      </body>
    </html>
  );
}
