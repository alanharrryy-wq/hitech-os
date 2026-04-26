import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { getOutboxConsole } from "@/lib/services/sync";

export const dynamic = "force-dynamic";

export default async function Page() {
  const outbox = await getOutboxConsole();

  return (
    <AppShell currentPath="/outbox-operativo">
      <section className="hero">
        <div className="kicker">capa i05</div>
        <h1 style={{ margin: 0 }}>Outbox operativo</h1>
        <div className="subtle">Cola de salida visible para revisar pendientes y fallos.</div>
      </section>
      <SectionCard title="Estado de la cola" subtitle="Resumen por status.">
        <div className="list">
          {outbox.outboxStatusSummary.map((item) => (
            <div key={item.status} className="list-item">{item.status}: {item.total} eventos</div>
          ))}
        </div>
      </SectionCard>
      <SectionCard title="Pendientes recientes" subtitle="Muestra de outbox pendiente o fallido.">
        <div className="list">
          {outbox.outboxPending.slice(0, 8).map((item) => (
            <div key={item.id} className="list-item">{item.topic} · {item.status} · {item.aggregateId}</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
