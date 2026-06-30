import { GalleryChrome, loadTabletGallerySource } from "../_tablet-gallery-runtime";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletReportSurfaceV2 } from "@components/tablet-visual-v2";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "PRISMA Tablet Codex Gallery",
  description: "Galería real de Visual OS para revisar glass panels, codex presets, motion, rim, glow y bundles en Tablet Light."
};

export default function TabletCodexGalleryPage() {
  const gallery = loadTabletGallerySource({
    title: "Tablet Codex Glass Gallery",
    description: "Ruta real para revisar la galería codex-native de paneles, vidrio, rim, glow, motion, bundles y capacidades visuales de Tablet sin tocar el POS productivo.",
    routePath: "/visual-os/tablet-codex-gallery",
    htmlFiles: ["tablet-codex-glass-gallery-smoke-test.html"],
    requiredJsonFiles: ["tablet-codex-glass-gallery.demo.json", "visual-verifier-rules.json", "tablet-light-preset.schema.json"]
  });

  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os/tablet-codex-gallery"
      title="Codex Gallery"
      subtitle="Galería de paneles, vidrio, rim, glow, motion y capacidades visuales."
      kicker="Visual OS"
    >
      <TabletReportSurfaceV2 routeId="/visual-os/tablet-codex-gallery" title="Codex Gallery" description="Galería de paneles, vidrio, rim, glow, motion y capacidades visuales." statusLabel="Gallery">
        <GalleryChrome gallery={gallery} />
      </TabletReportSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
