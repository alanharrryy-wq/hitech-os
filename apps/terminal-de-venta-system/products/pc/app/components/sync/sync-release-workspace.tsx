import type { TriDbStatusCardModel } from "../../src/modules/sync/tri-db-status.types";
import { TriDbStatusCard } from "./tri-db-status-card";
import { TriDbSyncAction } from "./tri-db-sync-action";

export function SyncReleaseWorkspace({ triDbStatus }: { triDbStatus: TriDbStatusCardModel }) {
  return (
    <main style={{ minHeight: "100vh", padding: "clamp(14px, 3vw, 32px)" }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ marginBottom: 18 }}>
          <div style={{ fontSize: 12, fontWeight: 950, letterSpacing: ".14em", textTransform: "uppercase" }}>PRISMA PC</div>
          <h1 style={{ fontSize: "clamp(1.7rem, 5vw, 2.55rem)", letterSpacing: 0, lineHeight: 1.04, margin: "8px 0" }}>Sincronizacion y estado operativo</h1>
          <p style={{ lineHeight: 1.5, maxWidth: 760 }}>Control visible para confirmar que Tablet, PC canonical y Mobile hablan sobre la misma verdad operativa, con evidencia legible y sin volcar trazas tecnicas en la primera lectura.</p>
        </div>
        <TriDbSyncAction />
        <TriDbStatusCard status={triDbStatus} />
      </div>
    </main>
  );
}
