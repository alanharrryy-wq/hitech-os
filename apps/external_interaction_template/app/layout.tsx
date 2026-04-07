import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AmbientBackdrop } from "@components/layout/ambient-backdrop";
import { AppFrame } from "@components/layout/app-frame";

import "./globals.css";

export const metadata: Metadata = {
  title: "External Interaction Template",
  description: "Domain-neutral external interaction template for collect, review, update, approve, dispatch and sync flows."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AmbientBackdrop />
        <div className="pointer-events-none fixed inset-0 -z-10 grid-fade" />
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
