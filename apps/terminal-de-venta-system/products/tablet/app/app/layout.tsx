import "./globals.css";
import "./prisma-tablet-softglass-canonical.css";
import { headers } from "next/headers";
import { PRISMA_TABLET_VISUAL_V2 } from "../components/tablet-visual-v2/tablet-visual-tokens";
import visualRootStyles from "../components/tablet-visual-v2/tablet-visual-v2-root.module.css";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: tabletMessages.metadata.title,
  description: tabletMessages.metadata.description
};

function normalizePrismaRoute(value: string | null) {
  const route = value && value.startsWith("/") ? value : "/";
  return route.length > 1 ? route.replace(/\/+$/, "") : route;
}

function prismaRoutePanelId(route: string) {
  if (route === "/") return "tablet.root.route";
  return `tablet.${route.slice(1).replace(/[^A-Za-z0-9]+/g, ".").replace(/^\.|\.$/g, "")}.route`;
}

export default async function RootLayout({ children }: { children: any }) {
  const route = normalizePrismaRoute((await headers()).get("x-prisma-route"));
  const canonicalViewport = `${PRISMA_TABLET_VISUAL_V2.canonicalViewport.width}x${PRISMA_TABLET_VISUAL_V2.canonicalViewport.height}@${PRISMA_TABLET_VISUAL_V2.canonicalViewport.zoom}`;

  return (
    <html
      lang="es-MX"
      data-prisma-skin="light"
      data-prisma-surface="tablet-softglass"
      data-theme="prisma-light"
      data-prisma-visual-mode="softglass-reference"
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
      data-prisma-canonical-viewport={canonicalViewport}
      data-prisma-canonical-shell="softglass-reference-2606"
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var root=document.documentElement;root.dataset.prismaSkin="light";root.dataset.theme="prisma-light";root.dataset.prismaSurface="tablet-softglass";root.dataset.prismaVisualMode="softglass-reference";root.dataset.prismaVisualV2="${PRISMA_TABLET_VISUAL_V2.dataAttribute}";root.dataset.prismaCanonicalViewport="${canonicalViewport}";root.dataset.prismaCanonicalShell="softglass-reference-2606";}catch(e){}})();`
          }}
        />
      </head>
      <body
        className={visualRootStyles.visualRoot}
        data-prisma-panel={prismaRoutePanelId(route)}
        data-prisma-surface="tablet"
        data-prisma-route={route}
        data-prisma-softglass-canonical="true"
        data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
        data-prisma-canonical-viewport={canonicalViewport}
      >
        {children}
      </body>
    </html>
  );
}
