import { InventoryWorkspace } from "@components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function InventoryPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return (
    <div
      data-prisma-panel="tablet.inventory.route"
      data-prisma-surface="tablet"
      data-prisma-route="/inventory"
    >
      <InventoryWorkspace currentPath="/inventory" runtimeSnapshot={runtimeSnapshot} />
    </div>
  );
}
