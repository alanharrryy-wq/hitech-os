// PRISMA_CTX_WEB_EIT_GENERATED_V1
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA EIT",
  description: "Executive Intelligence Terminal for PRISMA operational intelligence.",
  icons: {
    icon: "/prisma-mark.png",
    apple: "/prisma-mark.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <div className="prisma-global-logo-badge" aria-label="PRISMA">
          <img src="/prisma-mark.png" alt="" aria-hidden="true" />
          <span>PRISMA</span>
        </div>
        {children}
      </body>
    </html>
  );
}
