import { GalleryChrome, loadTabletGallerySource } from "../_tablet-gallery-runtime";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "PRISMA Materiality Catalog · Visual OS Pilot 01",
  description:
    "Piloto controlado del Surface Visual Governor: Materiality Catalog, Atmosphere Engine, Double Glass, Hydro Rim y route budgets. Visual OS only. No toca POS."
};

export default function PrismaMaterialityCatalogPage() {
  const gallery = loadTabletGallerySource({
    title: "PRISMA Materiality Catalog",
    description:
      "Ruta Visual OS para revisar el catálogo de materialidad fusionado: fondos reales, double glass, hydro rim, motion gobernado, route budgets y documentación preservada. Esta ruta no modifica POS ni pantallas productivas.",
    routePath: "/visual-os/materiality-catalog",
    htmlFiles: ["materiality-catalog-preview.html"],
    requiredJsonFiles: [
      "prisma.materiality-catalog.registry.3000-3150.json",
      "surface-visual-governor.pilot-01.json"
    ]
  });

  return <GalleryChrome gallery={gallery} />;
}
