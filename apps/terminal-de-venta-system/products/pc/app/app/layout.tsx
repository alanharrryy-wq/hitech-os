import type { ReactNode } from "react";
import "./globals.css";
import "./pc-atmosphere-clean.css";
import "./suppliers-ux-v08.css";
import { headers } from "next/headers";
import { PrismaAtmosphericBackground } from "./components/PrismaAtmosphericBackground";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PrismaDevIssueBadgeCleaner } from "./prisma-dev-issue-badge-cleaner";
import styles from "./layout.module.css";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

const prismaSkinBootstrap = `
(function () {
  try {
    var root = document.documentElement;
    root.dataset.prismaSkin = "tactical";
    root.dataset.prismaSurface = "pc-backoffice";
    root.dataset.theme = "prisma-command-center";
    root.dataset.prismaSkinPreference = "tactical";
  } catch (error) {
    document.documentElement.dataset.prismaSkin = "tactical";
    document.documentElement.dataset.prismaSurface = "pc-backoffice";
    document.documentElement.dataset.theme = "prisma-command-center";
    document.documentElement.dataset.prismaSkinPreference = "tactical";
  }
})();
`;

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

  return (
    <html
      lang="es-MX"
      data-theme="prisma-command-center"
      data-prisma-skin="tactical"
      data-prisma-skin-preference="tactical"
      data-prisma-surface="pc-backoffice"
      data-prisma-visual-os="PC_UNIFIED_COMMAND_CENTER_0307"
      data-prisma-vos-binding="UCC-0307"
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: prismaSkinBootstrap }} />
      </head>
      <body
        className={styles.body}
        data-prisma-panel={prismaRoutePanelId(route)}
        data-prisma-surface="pc"
        data-prisma-route={route}
      >
        <div className={styles.runtimeHost} data-prisma-layer="runtime">
          <PrismaDevIssueBadgeCleaner />
        </div>
        <div className={styles.backgroundHost} data-prisma-layer="background" aria-hidden="true">
          <PrismaAtmosphericBackground />
        </div>
        <div className={`prisma-app-content ${styles.appContent}`} data-prisma-layer="content">
          {children}
        </div>
        <div id="prisma-overlay-root" className={styles.overlayRoot} data-prisma-layer="overlay-root" aria-live="polite" />
      </body>
    </html>
  );
}
