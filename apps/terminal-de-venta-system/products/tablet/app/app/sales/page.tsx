import { SalesWorkspace } from "@components/sales/sales-workspace";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function SalesPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <SalesWorkspace view="today" runtimeSnapshot={runtimeSnapshot} />;
}
