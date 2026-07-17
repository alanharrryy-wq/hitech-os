import "./globals.css";
import "./prisma-tablet-nocturne-canonical.css";
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
      data-prisma-skin="dark"
      data-prisma-surface="tablet-nocturne"
      data-theme="prisma-nocturne"
      data-prisma-visual-mode="nocturnal-translucent"
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
      data-prisma-canonical-viewport={canonicalViewport}
      data-prisma-canonical-shell="nocturne-reference-1607"
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var root=document.documentElement;root.dataset.prismaSkin="dark";root.dataset.theme="prisma-nocturne";root.dataset.prismaSurface="tablet-nocturne";root.dataset.prismaVisualMode="nocturnal-translucent";root.dataset.prismaVisualV2="${PRISMA_TABLET_VISUAL_V2.dataAttribute}";root.dataset.prismaCanonicalViewport="${canonicalViewport}";root.dataset.prismaCanonicalShell="nocturne-reference-1607";}catch(e){}})();`
          }}
        />
      </head>
      <body
        className={visualRootStyles.visualRoot}
        data-prisma-panel={prismaRoutePanelId(route)}
        data-prisma-surface="tablet"
        data-prisma-route={route}
        data-prisma-nocturne-canonical="true"
        data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
        data-prisma-canonical-viewport={canonicalViewport}
      >
        {children}
      </body>
    </html>
  );
}
