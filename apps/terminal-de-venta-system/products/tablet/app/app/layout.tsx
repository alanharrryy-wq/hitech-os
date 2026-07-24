import "../generated/prisma-visual-runtime/prisma-tablet-runtime.css";
import { headers } from "next/headers";
import { PRISMA_TABLET_VISUAL_RUNTIME } from "../generated/prisma-visual-runtime/visual-values";
import visualRootStyles from "../generated/prisma-visual-runtime/prisma-runtime-root.module.css";
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
  const canonicalViewport = `${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.width}x${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.height}@${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.zoom}`;

  return (
    <html
      lang="es-MX"
      data-prisma-skin="dark"
      data-prisma-surface="tablet-rifat-atlas"
      data-theme="prisma-rifat-atlas"
      data-prisma-visual-mode="rifat-atlas-canonical"
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_RUNTIME.dataAttribute}
      data-prisma-canonical-viewport={canonicalViewport}
      data-prisma-canonical-shell="rifat-atlas-tablet-v1"
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var root=document.documentElement;root.dataset.prismaSkin="dark";root.dataset.theme="prisma-rifat-atlas";root.dataset.prismaSurface="tablet-rifat-atlas";root.dataset.prismaVisualMode="rifat-atlas-canonical";root.dataset.prismaVisualV2="${PRISMA_TABLET_VISUAL_RUNTIME.dataAttribute}";root.dataset.prismaCanonicalViewport="${canonicalViewport}";root.dataset.prismaCanonicalShell="rifat-atlas-tablet-v1";}catch(e){}})();`
          }}
        />
      </head>
      <body
        className={visualRootStyles.visualRoot}
        data-prisma-panel={prismaRoutePanelId(route)}
        data-prisma-surface="tablet"
        data-prisma-route={route}
        data-prisma-rifat-canonical="true"
        data-prisma-visual-v2={PRISMA_TABLET_VISUAL_RUNTIME.dataAttribute}
        data-prisma-canonical-viewport={canonicalViewport}
      >
        {children}
      </body>
    </html>
  );
}
