import { SellingWorkspace } from "@components/pos/pos-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Vender - PRISMA Tablet",
  description: "Caja rápida touch-first para buscar, agregar y preparar el cobro."
};

export default async function PosPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <SellingWorkspace runtimeSnapshot={runtimeSnapshot} />;
}
