import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, Manrope, Space_Grotesk } from "next/font/google";
import type { ReactNode } from "react";

import { AmbientBackdrop } from "@components/layout/ambient-backdrop";
import { AppFrame } from "@components/layout/app-frame";

import "./globals.css";

export const metadata: Metadata = {
  title: "External Interaction Template",
  description: "Plantilla neutral para interacciones externas con flujos de captura, revisión, actualización, aprobación, despacho y sincronización."
};

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap"
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap"
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap"
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
  weight: ["400", "500"]
});

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body className={`${manrope.variable} ${fraunces.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}>
        <AmbientBackdrop />
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
