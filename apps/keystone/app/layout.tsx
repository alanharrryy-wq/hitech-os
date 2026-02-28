import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@hitech/ui-kit/styles.css";
import "./globals.css";
import { AppProviders } from "../providers/app-providers";

export const metadata: Metadata = {
  title: "Keystone Mission Control",
  description: "HITECH OS Keystone web-first premium-ready skeleton"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
