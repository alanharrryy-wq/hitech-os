import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { formatLatency } from "@/lib/i05/replenishment-sync-helpers";
import { getOutboxConsole } from "@/lib/services/sync";

export const dynamic = "force-dynamic";

export default async function Page() {
  const outbox = await getOutboxConsole();
  const maxAgeSeconds = Math.max(0, ...outbox.outboxPending.map((item) => Number.parseInt(item.age, 10) || 0));

  return (
    <AppShell currentPath="/sync-operativo">
      <section className="hero">
        <div className="kicker">capa i05</div>
        <h1 style={{ margin: 0 }}>Sync operativo</h1>
        <div className="subtle">Visión operativa de eventos compartidos y latencia estimada.</div>
      </section>
      <SectionCard title="Latencia" subtitle="Señal rápida de salud de sincronización.">
        <div className="list">
          <div className="list-item">Pendientes: {outbox.outboxPending.length}</div>
          <div className="list-item">Pico: {formatLatency(maxAgeSeconds)}</div>
        </div>
      </SectionCard>
      <SectionCard title="Eventos compartidos vigilados" subtitle="Contrato visible para PC y Tablet.">
        <div className="list">
          {outbox.outboxPending.map((item) => <div key={item.id} className="list-item">{item.topic} · {item.status} · {item.aggregateId}</div>)}
        </div>
      </SectionCard>
    </AppShell>
  );
}
