export const metadata = { title: "Historial de ventas - PRISMA Tablet", description: "Busca tickets anteriores y revisa su detalle." };
import { SalesHistoryScreen } from "@components/sales/sales-history-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function Page() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <SalesHistoryScreen runtimeSnapshot={runtimeSnapshot} />;
}
