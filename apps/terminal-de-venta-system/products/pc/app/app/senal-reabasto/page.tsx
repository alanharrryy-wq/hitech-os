import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { badgeForPriority } from "@/lib/i05/replenishment-sync-helpers";
import { getReplenishmentConsole } from "@/lib/services/sync";

export const dynamic = "force-dynamic";

export default async function Page() {
  const replenishment = await getReplenishmentConsole();

  return (
    <AppShell currentPath="/senal-reabasto">
      <section className="hero">
        <div className="kicker">capa i05</div>
        <h1 style={{ margin: 0 }}>Señal de reabasto</h1>
        <div className="subtle">Priorización operativa de reposición sin tocar el módulo base de Reabasto.</div>
      </section>
      <SectionCard title="Resumen por prioridad" subtitle="Lectura rápida para backoffice.">
        <div className="list">
          {replenishment.replenishmentSummary.map((item) => (
            <div key={item.priority} className="list-item">{badgeForPriority(item.priority)}: {item.total} señales · {item.qty} piezas sugeridas</div>
          ))}
        </div>
      </SectionCard>
      <SectionCard title="Señales con más filo" subtitle="Muestra de señales prioritarias.">
        <div className="list">
          {replenishment.topSignals.slice(0, 8).map((item) => (
            <div key={item.id} className="list-item">{item.sku} · {item.location} · prioridad {badgeForPriority(item.priority)} · sugerido {item.suggestedQty}</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
