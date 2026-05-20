import { CatalogStockSellingAssistScreen } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Existencias - PRISMA Tablet",
  description: "Alias operativo de stock con venta asistida desde inventario local."
};

export default async function ExistenciasPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <CatalogStockSellingAssistScreen mode="stock" runtimeSnapshot={runtimeSnapshot} />;
}
