import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISMA Chart Lab",
  description: "Canonical visual workshop for PRISMA ECharts operational charts.",
  // PRISMA_CAUSAL_FLOW_PREMIUM_PATCH_V2: keep public demos console-clean.
  // PRISMA_CHART_LAB_BRAND_LOGO_V1: local Chart Lab brand icon.
  icons: {
    icon: "/brand/prisma-prism-mark-192.png",
    shortcut: "/brand/prisma-prism-mark-192.png",
    apple: "/brand/prisma-prism-mark-192.png"
  }
};

function normalizePrismaRoute(value: string | null) {
  const route = value && value.startsWith("/") ? value : "/";
  return route.length > 1 ? route.replace(/\/+$/, "") : route;
}

function prismaRoutePanelId(route: string) {
  if (route === "/") return "chart-lab.root.route";
  return `chart-lab.${route.slice(1).replace(/[^A-Za-z0-9]+/g, ".").replace(/^\.|\.$/g, "")}.route`;
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const route = normalizePrismaRoute((await headers()).get("x-prisma-route"));

  return (
    <html lang="es-MX">
      <body data-prisma-panel={prismaRoutePanelId(route)} data-prisma-surface="chart-lab" data-prisma-route={route}>{children}</body>
    </html>
  );
}
