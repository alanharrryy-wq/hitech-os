import "./globals.css";
import { pcMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

export default function RootLayout({ children }: { children: any }) {
  return (
    <html lang="es-MX">
      <body>{children}</body>
    </html>
  );
}
