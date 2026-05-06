import "./globals.css";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: tabletMessages.metadata.title,
  description: tabletMessages.metadata.description
};

export default function RootLayout({ children }: { children: any }) {
  const prismaTheme = process.env.NEXT_PUBLIC_PRISMA_THEME === "prisma-light" ? "prisma-light" : "prisma-dark";

  return (
    <html lang="es-MX" data-theme={prismaTheme}>
      <body>{children}</body>
    </html>
  );
}
