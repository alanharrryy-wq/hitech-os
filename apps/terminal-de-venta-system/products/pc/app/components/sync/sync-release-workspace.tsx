import type { TriDbStatusCardModel } from "../../src/modules/sync/tri-db-status.types";
import { TriDbStatusCard } from "./tri-db-status-card";
import { TriDbSyncAction } from "./tri-db-sync-action";

export function SyncReleaseWorkspace({ triDbStatus }: { triDbStatus: TriDbStatusCardModel }) {
  return (
    <main style={{ minHeight: "100vh", padding: 32, background: "#020617" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ marginBottom: 18 }}>
          <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 900, letterSpacing: ".14em", textTransform: "uppercase" }}>PRISMA PC</div>
          <h1 style={{ color: "#f8fafc", fontSize: 38, margin: "8px 0" }}>Sincronizacion y estado operativo</h1>
          <p style={{ color: "#cbd5e1", maxWidth: 760 }}>Control visible para confirmar que Tablet, PC canonical y Mobile hablan sobre la misma verdad operativa.</p>
        </div>
        <TriDbSyncAction />
        <TriDbStatusCard status={triDbStatus} />
      </div>
    </main>
  );
}
