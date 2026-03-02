import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { HeatStrip, StatusChip } from "@hitech/ui-kit";
import "@hitech/ui-kit/styles.css";
import "./globals.css";
import { AppProviders } from "../providers/app-providers";
import { HitechLogo } from "../components/brand";

export const metadata: Metadata = {
  title: "Keystone Mission Control",
  description: "HITECH OS Keystone web-first premium-ready skeleton"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="ui-hitech-theme">
        <div className="keystone-app-shell">
          <header className="keystone-app-topbar">
            <Link href="/" aria-label="Go to Keystone home" className="keystone-app-brand">
              <HitechLogo />
            </Link>
            <nav className="keystone-app-nav" aria-label="Primary">
              <Link href="/" className="keystone-app-nav-link">
                Mission
              </Link>
              <Link href="/pitch" className="keystone-app-nav-link">
                Pitch
              </Link>
            </nav>
            <div className="keystone-app-meter" aria-label="System pulse">
              <HeatStrip values={[44, 58, 61, 73, 69, 82, 88, 79, 72, 67, 62, 74]} />
            </div>
            <StatusChip status="pass" label="CONTROL ROOM READY" className="keystone-app-status" />
          </header>
          <AppProviders>{children}</AppProviders>
        </div>
      </body>
    </html>
  );
}
