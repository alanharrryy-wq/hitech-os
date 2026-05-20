import { ShiftCashClosureScreen } from "@components/shift/shift-cash-closure-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";
export const metadata = { title: "Turno y caja - PRISMA Tablet", description: "Apertura, caja inicial, conteo y corte operativo local." };

export default async function ShiftPage() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <ShiftCashClosureScreen runtimeSnapshot={runtimeSnapshot} />;
}
