import "./globals.css";
import "./suppliers-ux-v08.css";
import "./prisma-visual-os-pc-binding.css";
import { pcMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

export default function RootLayout({ children }: { children: any }) {
  const prismaTheme = process.env.NEXT_PUBLIC_PRISMA_THEME === "prisma-light" ? "prisma-light" : "prisma-dark";

  return (
    <html lang="es-MX" data-theme={prismaTheme} data-prisma-surface="pc-backoffice" data-prisma-visual-os="PC_DENSE_ADMIN" data-prisma-vos-binding="00J">
      <body>{children}</body>
    </html>
  );
}
