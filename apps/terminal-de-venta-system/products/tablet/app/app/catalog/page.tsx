import { CatalogScreen } from "@components/catalog/catalog-screen";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Catálogo - PRISMA Tablet",
  description: "Buscar, registrar y editar productos locales para venta en Tablet."
};

export default function CatalogPage() {
  return <CatalogScreen />;
}
