import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { getProcurementConsole } from "@/lib/services/procurement";

export const dynamic = "force-dynamic";

export default async function Page() {
  const { stats, receivingIncidents } = await getProcurementConsole();

  return (
    <AppShell currentPath="/receiving">
      <section className="hero">
        <div className="kicker">i04 · recepción</div>
        <h1 style={{ margin: 0 }}>Recepción proveedor</h1>
        <div className="subtle">Confirmación física, incidencias y trazabilidad ligera para entradas de mercancía.</div>
      </section>
      <section style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <StatCard label="Incidencias" value={String(stats.recepcionesConIncidencia)} note="recibos con bandera de incidente" />
        <StatCard label="Líneas planeación" value={String(stats.lineasPlaneacion)} note="PurchaseOrderLine canónico" />
      </section>
      <SectionCard title="Recepciones calientes" subtitle="Lo que merece atención antes de que se esconda bajo la alfombra">
        <div className="list">{receivingIncidents.map((item) => <div key={item.folio} className="list-item">{item.folio} · {item.supplier} · {item.lines} líneas · ${item.total} · {item.receivedAt}</div>)}</div>
      </SectionCard>
    </AppShell>
  );
}
