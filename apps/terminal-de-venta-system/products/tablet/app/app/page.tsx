import { TabletHomeScreen } from "@components/tablet-home/tablet-home-screen";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletHomeSurfaceV2 } from "@components/tablet-visual-v2";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Inicio - PRISMA Tablet",
  description: "Tablero operativo de venta, caja, tickets, existencias y sincronización."
};

function pendingCount(snapshot: Awaited<ReturnType<typeof getTabletRuntimeSnapshot>>) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export default async function TabletHomePage() {
  const snapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  const pending = pendingCount(snapshot);
  const shiftOpen = snapshot.shift.state === "open";

  return (
    <PrismaTabletShellUnified
      currentPath="/"
      title="Inicio operativo"
      subtitle="Caja, ventas, tickets, existencias, sincronización y respaldo en una sola red de trabajo."
      kicker={snapshot.identity.storeName}
      status={
        <TabletShellStatusPill tone={shiftOpen ? (pending ? "warn" : "ok") : "warn"}>
          {shiftOpen ? (pending ? `${pending} pendiente(s)` : "Lista para vender") : "Caja cerrada"}
        </TabletShellStatusPill>
      }
      runtimeSnapshot={snapshot}
    >
      <TabletHomeSurfaceV2 routeId="/" title="Inicio operativo" description="Accesos principales de caja, ventas, stock y sincronización con lectura rápida para la Tablet." statusLabel={shiftOpen ? "Venta activa" : "Abrir caja"}>
        <TabletHomeScreen snapshot={snapshot} />
      </TabletHomeSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
