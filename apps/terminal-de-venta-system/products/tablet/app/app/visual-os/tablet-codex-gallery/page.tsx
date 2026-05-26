import { GalleryChrome, loadTabletGallerySource } from "../_tablet-gallery-runtime";

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

  return <GalleryChrome gallery={gallery} />;
}
