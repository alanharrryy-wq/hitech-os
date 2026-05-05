import { CatalogStockSellingAssistScreen } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Existencias - PRISMA Tablet",
  description: "Alias operativo de stock con venta asistida desde inventario local."
};

export default function ExistenciasPage() {
  return <CatalogStockSellingAssistScreen mode="stock" />;
}
