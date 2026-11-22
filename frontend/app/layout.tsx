import StreakChip from "@/components/StreakChip";
import Logo from "@/components/Logo";
import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";
import ThemeToggle from "@/components/ThemeToggle";
import LoadingIndicator from "@/components/LoadingIndicator";
import NavLinks from "@/components/NavLinks";
import AccountMenu from "@/components/AccountMenu";
import { PaletteButton } from "@/components/CommandPalette";
import MockBar from "@/components/MockBar";
import PwaRegister from "@/components/PwaRegister";
import { ACCENT_BOOT_SCRIPT } from "@/lib/appearance";
import CommandPalette from "@/components/CommandPalette";
import MobileTabBar from "@/components/MobileTabBar";

export const metadata: Metadata = {
  title: "LeetCode Practice", description: "Practice coding problems",
  icons: { icon: "/icon-192.png", apple: "/icon-192.png" },
  appleWebApp: { capable: true, title: "LeetCode", statusBarStyle: "black-translucent" },
};
export const viewport: Viewport = { themeColor: "#1a1a1a", width: "device-width", initialScale: 1, viewportFit: "cover" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* The code editor (Monaco) is fetched from this CDN when a problem opens; connect early so it starts sooner. */}
        <link rel="preconnect" href="https://cdn.jsdelivr.net" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />
        {/* Apply the saved theme before first paint so there is no flash of the wrong theme. */}
        <script dangerouslySetInnerHTML={{ __html:
          "try{if(localStorage.getItem('lc-theme')==='light')document.documentElement.dataset.theme='light'}catch(e){}" + ACCENT_BOOT_SCRIPT +
          // Start waking the (free-tier) backend the moment the page arrives, before any app code runs.
          `try{fetch(${JSON.stringify((process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080") + "/actuator/health")},{mode:'no-cors',keepalive:true})}catch(e){}` }} />
      </head>
      <body>
        <a href="#main" className="skip-link">Skip to content</a>
        <header className="nav">
          <Link href="/" className="brand" aria-label="LeetCode Practice home"><Logo size={30} /><span className="brand-text"> LeetCode Practice</span></Link>
          <nav><LoadingIndicator /><NavLinks /></nav>
          {/* Fixed cluster: lives outside the scrolling link list, so Profile never moves. */}
          <div className="nav-end"><PaletteButton /><StreakChip /><ThemeToggle /><AccountMenu /></div>
        </header>
        <PwaRegister />
        <MockBar />
        <main id="main" tabIndex={-1}>{children}</main>
        <MobileTabBar />
        <CommandPalette />
      </body>
    </html>
  );
}
