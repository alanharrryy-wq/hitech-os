import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import {
  BrandPresenceLayer,
  HitechLogo,
  brandPresenceConfig,
  createBrandPresenceRootStyle
} from "@hitech/ui-kit";
import "@hitech/ui-kit/styles.css";
import "./globals.css";
import { AppProviders } from "../providers/app-providers";

export const metadata: Metadata = {
  title: "Keystone Mission Control",
  description: "HITECH OS Keystone web-first premium-ready skeleton"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const brandStyle = createBrandPresenceRootStyle("neutral", "subtle");
  const showSceneStudioLink = process.env["NODE_ENV"] !== "production";

  return (
    <html lang="en">
      <body className="ui-hitech-theme" style={brandStyle}>
        <AppProviders>
          <div className="keystone-app-shell hitech-brand-shell-depth">
            {brandPresenceConfig.enableGlobalWatermark ? (
              <BrandPresenceLayer
                mode="watermark"
                intensity="subtle"
                profile="neutral"
                repeatPattern
                className="keystone-app-watermark"
              />
            ) : null}
            <header className="keystone-app-topbar">
              <Link href="/" className="keystone-app-brand" aria-label="Go to Keystone home">
                <span className="keystone-app-brand-mark-wrap">
                  {brandPresenceConfig.enableHeaderMark ? (
                    <BrandPresenceLayer
                      mode="header-mark"
                      intensity="subtle"
                      profile="neutral"
                      className="keystone-app-header-mark"
                    />
                  ) : null}
                  <HitechLogo className="keystone-app-logo" />
                </span>
              </Link>
              <nav className="keystone-app-nav" aria-label="Primary">
                <Link href="/" className="keystone-app-nav-link">
                  Mission
                </Link>
                <Link href="/pitch" className="keystone-app-nav-link">
                  Pitch
                </Link>
                {showSceneStudioLink ? (
                  <Link href="/dev/scene-studio?debug=1" className="keystone-app-nav-link">
                    Scene Studio
                  </Link>
                ) : null}
              </nav>
            </header>
            <main className="keystone-app-main">{children}</main>
            {brandPresenceConfig.enableFooterSignature ? (
              <footer className="hitech-brand-signature keystone-app-signature">
                HITech - Deterministic Systems
              </footer>
            ) : null}
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
