import { PosScreen } from "@components/pos/pos-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Cobro unificado - PRISMA Tablet",
  description: "El cobro usa el mismo motor del POS para evitar dos flujos de venta."
};

export default async function CheckoutPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <PosScreen runtimeSnapshot={runtimeSnapshot} />;
}
