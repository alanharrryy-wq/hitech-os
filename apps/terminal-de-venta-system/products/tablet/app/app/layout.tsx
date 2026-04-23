import "./globals.css";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: tabletMessages.metadata.title,
  description: tabletMessages.metadata.description
};

export default function RootLayout({ children }: { children: any }) {
  return (
    <html lang="es-MX">
      <body>{children}</body>
    </html>
  );
}
