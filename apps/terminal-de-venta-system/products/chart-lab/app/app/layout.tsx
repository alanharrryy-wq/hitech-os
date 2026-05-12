import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA Chart Lab",
  description: "Canonical visual workshop for PRISMA ECharts operational charts.",
  // PRISMA_CAUSAL_FLOW_PREMIUM_PATCH_V2: keep public demos console-clean.
  icons: {
    icon: "/favicon.svg"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX">
      <body>{children}</body>
    </html>
  );
}
