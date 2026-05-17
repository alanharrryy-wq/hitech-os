// PRISMA_CTX_WEB_EIT_GENERATED_V1
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA EIT | Knowledge OS operativo",
  description: "PRISMA convierte operaciones reales en contexto auditable, alertas accionables y gobierno operativo.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
