import "./globals.css";
import "./suppliers-ux-v08.css";
import "./prisma-visual-os-pc-binding.css";
import "./prisma-atmospheric-background.css";
import "./prisma-pc-premium-visual-system.css";
import { headers } from "next/headers";
import { PrismaAtmosphericBackground } from "./components/PrismaAtmosphericBackground";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PrismaSurfFix6LifecycleRuntime } from "./prisma-surf-fix6-lifecycle-runtime";
import { PrismaDevIssueBadgeCleaner } from "./prisma-dev-issue-badge-cleaner";
import { PrismaPcPremiumRuntime } from "./components/PrismaPcPremiumRuntime";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

const prismaSkinBootstrap = `
(function () {
  try {
    var root = document.documentElement;
    root.dataset.prismaSkin = "light";
    root.dataset.prismaSurface = "pc-backoffice";
    root.dataset.theme = "prisma-light";
    root.dataset.prismaSkinPreference = "light";
  } catch (error) {
    document.documentElement.dataset.prismaSkin = "light";
    document.documentElement.dataset.prismaSurface = "pc-backoffice";
    document.documentElement.dataset.theme = "prisma-light";
    document.documentElement.dataset.prismaSkinPreference = "light";
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

export default async function RootLayout({ children }: { children: any }) {
  const route = normalizePrismaRoute((await headers()).get("x-prisma-route"));

  return (
    <html
      lang="es-MX"
      data-theme="prisma-light"
      data-prisma-skin="light"
      data-prisma-skin-preference="light"
      data-prisma-surface="pc-backoffice"
      data-prisma-visual-os="PC_PREMIUM_LIGHT_SYS1"
      data-prisma-vos-binding="00J"
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: prismaSkinBootstrap }} />
      </head>
      <body data-prisma-panel={prismaRoutePanelId(route)} data-prisma-surface="pc" data-prisma-route={route}>
        <PrismaDevIssueBadgeCleaner />
        <PrismaSurfFix6LifecycleRuntime />
        <PrismaAtmosphericBackground />
        <PrismaPcPremiumRuntime />
        <div className="prisma-app-content">{children}</div>
      </body>
    </html>
  );
}
