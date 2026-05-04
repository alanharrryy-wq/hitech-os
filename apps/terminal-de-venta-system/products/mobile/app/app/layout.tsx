import "./globals.css";
import "./prisma-mobile-pulse-binding.css";
import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { PrismaMobilePwaRuntime } from "@/components/prisma-app";

export const metadata: Metadata = {
  title: {
    default: "PRISMA App",
    template: "%s | PRISMA App",
  },
  applicationName: "PRISMA App",
  description:
    "App móvil independiente para consulta, pulso, alertas y reportes ligeros de negocio.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/icons/prisma_playstore_icon_192.png", type: "image/png", sizes: "192x192" },
      { url: "/icons/prisma_playstore_icon_512.png", type: "image/png", sizes: "512x512" },
      { url: "/apple-touch-icon.png", type: "image/png", sizes: "180x180" },
      { url: "/icons/prisma-app-icon.svg", type: "image/svg+xml" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", type: "image/png", sizes: "180x180" },
      { url: "/icons/prisma_playstore_icon_512.png", type: "image/png", sizes: "512x512" },
    ],
    shortcut: ["/apple-touch-icon.png"],
  },
  appleWebApp: {
    capable: true,
    title: "PRISMA App",
    statusBarStyle: "black-translucent",
  },
  formatDetection: {
    telephone: false,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  viewportFit: "cover",
  themeColor: "#07080d",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const prismaTheme =
    process.env.NEXT_PUBLIC_PRISMA_THEME === "prisma-light"
      ? "prisma-light"
      : "prisma-dark";

  return (
    <html lang="es-MX" data-theme={prismaTheme} data-prisma-surface="mobile-pulse" data-prisma-visual-os="MOBILE_PULSE" data-prisma-vos-binding="00K">
      <body>
        {children}
        <PrismaMobilePwaRuntime />
      </body>
    </html>
  );
}
