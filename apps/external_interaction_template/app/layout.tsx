import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA | Tablet opera, PC gobierna, Mobile supervisa",
  description:
    "PRISMA conecta punto de venta, administración y supervisión móvil para operar con menos caos y más control.",
  metadataBase: new URL("https://eit.hitechrts.com"),
  openGraph: {
    title: "PRISMA",
    description:
      "Vende en Tablet. Controla en PC. Supervisa desde el celular.",
    url: "https://eit.hitechrts.com",
    siteName: "PRISMA",
    images: [{ url: "/prisma/brand/prisma-og.svg", width: 1200, height: 630 }],
    locale: "es_MX",
    type: "website"
  }
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
