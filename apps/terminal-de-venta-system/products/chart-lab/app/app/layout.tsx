import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA Chart Lab",
  description: "Canonical visual workshop for PRISMA ECharts operational charts."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX">
      <body>{children}</body>
    </html>
  );
}
