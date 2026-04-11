import type { Metadata } from "next";
import { Cormorant_Garamond, Plus_Jakarta_Sans } from "next/font/google";
import type { ReactNode } from "react";
import { brandConfig } from "@/lib/config/brand";
import { getFormsPublicEnv } from "@/lib/config/env";
import "./globals.css";

const headingFont = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-forms-display",
  weight: ["500", "600", "700"]
});

const bodyFont = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-forms-body",
  weight: ["400", "500", "600", "700"]
});

export const metadata: Metadata = {
  title: brandConfig.appName,
  description: brandConfig.tagline,
  metadataBase: new URL(getFormsPublicEnv().publicAppUrl),
  alternates: {
    canonical: "/"
  }
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body className={`${headingFont.variable} ${bodyFont.variable} forms-root`}>{children}</body>
    </html>
  );
}
