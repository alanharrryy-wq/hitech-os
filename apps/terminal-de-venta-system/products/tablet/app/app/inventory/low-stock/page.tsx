import { InventoryWorkspace } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Stock bajo - PRISMA Tablet",
  description: "Productos locales que requieren reposición."
};

export default async function LowStockPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <InventoryWorkspace currentPath="/inventory/low-stock" intent="low-stock" runtimeSnapshot={runtimeSnapshot} />;
}
