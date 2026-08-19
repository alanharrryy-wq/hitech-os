import type { ReactNode } from "react";
import "./globals.css";
import "./suppliers-ux-v08.css";
import { headers } from "next/headers";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PcLicenseSurfaceProvider } from "@/components/licensing/pc-license-surface-provider";
import { resolvePcFeature } from "@/src/server/licensing/pc-license-service";
import { PrismaDevIssueBadgeCleaner } from "./prisma-dev-issue-badge-cleaner";
import styles from "./layout.module.css";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

function normalizePrismaRoute(value: string | null) {
  const route = value && value.startsWith("/") ? value : "/";
  return route.length > 1 ? route.replace(/\/+$/, "") : route;
}

function prismaRoutePanelId(route: string) {
  if (route === "/") return "pc.root.route";
  return `pc.${route.slice(1).replace(/[^A-Za-z0-9]+/g, ".").replace(/^\.|\.$/g, "")}.route`;
}

export default async function RootLayout({ children }: { children: ReactNode }) {
  const route = normalizePrismaRoute((await headers()).get("x-prisma-route"));
  const pcNavigationAllowed = resolvePcFeature("pc.open").allowed;

  return (
    <html lang="es-MX" data-prisma-surface="pc-backoffice" data-prisma-visual-os="PC_DENSE_ADMIN">
      <body
        className={styles.body}
        data-prisma-panel={prismaRoutePanelId(route)}
        data-prisma-surface="pc"
        data-prisma-route={route}
        data-prisma-pc-navigation={pcNavigationAllowed ? "allowed" : "denied"}
      >
        <div className={styles.runtimeHost} data-prisma-layer="runtime">
          <PrismaDevIssueBadgeCleaner />
        </div>
        <div className={styles.appContent} data-prisma-layer="content">
          <PcLicenseSurfaceProvider navigationAllowed={pcNavigationAllowed}>
            {children}
          </PcLicenseSurfaceProvider>
        </div>
        <div id="prisma-overlay-root" className={styles.overlayRoot} data-prisma-layer="overlay-root" aria-live="polite" />
      </body>
    </html>
  );
}
