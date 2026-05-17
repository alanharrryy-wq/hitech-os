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
import { externalAppLinks } from "../lib/config/external-app-links";

export const metadata: Metadata = {
  title: "Keystone Mission Control",
  description: "HITECH OS Keystone web-first premium-ready skeleton"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const brandStyle = createBrandPresenceRootStyle("neutral", "subtle");

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
                {externalAppLinks.showOperatorEntry ? (
                  <a
                    href={externalAppLinks.operatorAppUrl!}
                    target="_blank"
                    rel="noreferrer"
                    className="keystone-app-nav-link"
                  >
                    Operator UI
                  </a>
                ) : null}
                <a
                  href={externalAppLinks.formsAppUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="keystone-app-nav-link"
                >
                  Public Forms
                </a>
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
