import type { TriDbStatusCardModel } from "../../src/modules/sync/tri-db-status.types";
import { TriDbStatusCard } from "./tri-db-status-card";
import { TriDbSyncAction } from "./tri-db-sync-action";

export function SyncReleaseWorkspace({ triDbStatus }: { triDbStatus: TriDbStatusCardModel }) {
  return (
    <main style={{
      background: "radial-gradient(circle at 12% 6%, rgba(18,107,255,.12), transparent 24rem), linear-gradient(180deg, #f7fafe 0%, #eef3f8 62%, #e8eef6 100%)",
      color: "#102033",
      minHeight: "100vh",
      padding: "clamp(14px, 3vw, 32px)"
    }}>
      <div style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div style={{ marginBottom: 18 }}>
          <div style={{ color: "#126bff", fontSize: 12, fontWeight: 950, letterSpacing: ".14em", textTransform: "uppercase" }}>PRISMA PC</div>
          <h1 style={{ color: "#102033", fontSize: "clamp(1.7rem, 5vw, 2.55rem)", letterSpacing: 0, lineHeight: 1.04, margin: "8px 0" }}>Sincronizacion y estado operativo</h1>
          <p style={{ color: "#56677d", lineHeight: 1.5, maxWidth: 760 }}>Control visible para confirmar que Tablet, PC base principal y Mobile hablan sobre la misma verdad operativa, con evidencia legible y sin volcar trazas tecnicas en la primera lectura.</p>
        </div>
        <TriDbSyncAction />
        <TriDbStatusCard status={triDbStatus} />
      </div>
    </main>
  );
}
