import { CatalogStockSellingAssistScreen } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";
import { ContextualExportBand } from "@components/reports/contextual-export-band";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";
export const metadata = { title: "Existencias para vender - PRISMA Tablet", description: "Existencias operativas locales con bajo inventario, sin inventario, inactivos y envío al carrito de venta." };

export default async function StockPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <CatalogStockSellingAssistScreen actions={<ContextualExportBand surface="stock" />} mode="stock" runtimeSnapshot={runtimeSnapshot} />;
}
