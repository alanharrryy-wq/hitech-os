import { GalleryChrome, loadTabletGallerySource } from "../_tablet-gallery-runtime";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "PRISMA Tablet Storm Vapor Background Gallery",
  description:
    "Galería Visual OS para revisar Storm Real y Liquid Ops v14: imagen real de tormenta menos blanquecina, displacement vapor más visible, paneles con blur mínimo y fondo Liquid Ops basado en arte de referencia. No toca POS."
};

export default function TabletBackgroundGalleryPage() {
  const gallery = loadTabletGallerySource({
    title: "Tablet Storm Vapor Background Gallery",
    description:
      "Ruta real para revisar Storm Vapor Glass Cards v14: se eliminaron los glows naranja/verde/amarillo, se oscureció y cubrió mejor el fondo Storm Real, se aumentó la visibilidad del vapor displacement y Liquid Ops usa una imagen de referencia nueva. Visual OS only. No toca POS.",
    routePath: "/visual-os/tablet-background-gallery",
    htmlFiles: ["tablet-codex-background-gallery-smoke-test.html", "background-presets-smoke-test.html"],
    requiredJsonFiles: [
      "tablet-background-presets.light.json",
      "tablet-background-presets.light.patch.json",
      "tablet-background-presets.liquid-operations-v6.json",
      "tablet-background-presets.storm-glass-v14.json",
      "visual-verifier-rules.json"
    ]
  });

  return <GalleryChrome gallery={gallery} />;
}
