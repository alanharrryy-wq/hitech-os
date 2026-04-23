import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { procurementStats, receivingIncidents } from "@/lib/i04/procurement-data";

export default function Page() {
  return (
    <AppShell currentPath="/receiving">
      <section className="hero">
        <div className="kicker">i04 · recepción</div>
        <h1 style={{ margin: 0 }}>Recepción proveedor</h1>
        <div className="subtle">Confirmación física, incidencias y trazabilidad ligera para entradas de mercancía.</div>
      </section>
      <section style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
        <StatCard label="Incidencias" value={String(procurementStats.recepcionesConIncidencia)} note="recibos con bandera de incidente" />
        <StatCard label="Líneas planeación" value={String(procurementStats.lineasPlaneacion)} note="dataset útil para recepción futura" />
      </section>
      <SectionCard title="Recepciones calientes" subtitle="Lo que merece atención antes de que se esconda bajo la alfombra">
        <div className="list">{receivingIncidents.map((item) => <div key={item.purchaseId} className="list-item">{item.purchaseId} · {item.supplier} · {item.lines} líneas · {item.receivedAt}</div>)}</div>
      </SectionCard>
    </AppShell>
  );
}
