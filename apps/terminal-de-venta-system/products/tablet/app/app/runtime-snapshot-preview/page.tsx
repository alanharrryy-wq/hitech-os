import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletRuntimePanel } from "@components/tablet-runtime/tablet-runtime-panel";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";

export const dynamic = "force-dynamic";

export default async function RuntimeSnapshotPreviewPage() {
  const snapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  return (
    <PrismaTabletShellUnified
      currentPath="/"
      title="Estado operativo"
      subtitle="Una sola lectura para turno, conexion, pendientes, catalogo y ventas del dia."
      runtimeSnapshot={snapshot}
    >
      <div className="grid cols-2">
        <TabletRuntimePanel snapshot={snapshot} />
        <section className="card">
          <div className="kicker">Contrato 03B</div>
          <h2>Snapshot vivo de Tablet</h2>
          <p className="subtle">Este panel existe para probar la lectura operativa sin abrir DevTools ni perseguir logs como cucaracha con chancla.</p>
          <pre className="code" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify({ schemaVersion: snapshot.schemaVersion, shift: snapshot.shift.label, connection: snapshot.connection.label, catalog: snapshot.catalog.label, ticketsClosed: snapshot.sales.ticketsClosed }, null, 2)}</pre>
        </section>
      </div>
    </PrismaTabletShellUnified>
  );
}
