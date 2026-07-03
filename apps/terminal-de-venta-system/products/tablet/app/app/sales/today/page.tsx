export const metadata = { title: "Ventas de hoy - PRISMA Tablet", description: "Consulta tickets, totales y acciones de venta del día." };
import { SalesTodayScreen } from "@components/sales/sales-today-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function Page() {
  const runtimeSnapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return <SalesTodayScreen runtimeSnapshot={runtimeSnapshot} />;
}
