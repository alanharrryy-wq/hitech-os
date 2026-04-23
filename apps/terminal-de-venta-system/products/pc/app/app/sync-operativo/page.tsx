import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI05Data } from "@/lib/i05/replenishment-sync-data";
import { formatLatency } from "@/lib/i05/replenishment-sync-helpers";

export default function Page() {
  return (
    <AppShell currentPath="/sync-operativo">
      <section className="hero">
        <div className="kicker">capa i05</div>
        <h1 style={{ margin: 0 }}>Sync operativo</h1>
        <div className="subtle">Visión operativa de eventos compartidos y latencia estimada.</div>
      </section>
      <SectionCard title="Latencia" subtitle="Señal rápida de salud de sincronización.">
        <div className="list">
          <div className="list-item">Promedio: {formatLatency(Number(pcI05Data.avgLatencySeconds ?? 0))}</div>
          <div className="list-item">Pico: {formatLatency(Number(pcI05Data.maxLatencySeconds ?? 0))}</div>
        </div>
      </SectionCard>
      <SectionCard title="Eventos compartidos vigilados" subtitle="Contrato visible para PC y Tablet.">
        <div className="list">
          {pcI05Data.sharedEvents.map((item) => <div key={item} className="list-item">{item}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
