// PRISMA_CTX_WEB_EIT_GENERATED_V1
import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA EIT",
  description: "Executive Intelligence Terminal for PRISMA operational intelligence.",
  icons: {
    icon: "/prisma-mark.png",
    apple: "/prisma-mark.png",
  },
};

function normalizePrismaRoute(value: string | null) {
  const route = value && value.startsWith("/") ? value : "/";
  return route.length > 1 ? route.replace(/\/+$/, "") : route;
}

function prismaRoutePanelId(route: string) {
  if (route === "/") return "web.root.route";
  return `web.${route.slice(1).replace(/[^A-Za-z0-9]+/g, ".").replace(/^\.|\.$/g, "")}.route`;
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const route = normalizePrismaRoute((await headers()).get("x-prisma-route"));

  return (
    <html lang="es">
      <body data-prisma-panel={prismaRoutePanelId(route)} data-prisma-surface="web" data-prisma-route={route}>
        <div className="prisma-global-logo-badge" aria-label="PRISMA">
          <img src="/prisma-mark.png" alt="" aria-hidden="true" />
          <span>PRISMA</span>
        </div>
        {children}
      </body>
    </html>
  );
}
