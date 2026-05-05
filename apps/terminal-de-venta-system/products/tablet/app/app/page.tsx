import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletHomeScreen } from "@components/tablet-home/tablet-home-screen";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const snapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());

  return (
    <PrismaTabletShellUnified
      currentPath="/"
      kicker="Tablet vende sola"
      title="Inicio"
      subtitle="Estado real de caja, ventas, pendientes y existencias antes de operar."
      runtimeSnapshot={snapshot}
    >
      <TabletHomeScreen snapshot={snapshot} />
    </PrismaTabletShellUnified>
  );
}
