import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AmbientBackdrop } from "@components/layout/ambient-backdrop";
import { AppFrame } from "@components/layout/app-frame";

import "./globals.css";

export const metadata: Metadata = {
  title: "External Interaction Template",
  description: "Plantilla neutral para interacciones externas con flujos de captura, revisión, actualización, aprobación, despacho y sincronización."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <AmbientBackdrop />
        <div className="pointer-events-none fixed inset-0 -z-10 grid-fade" />
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
