import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { pcI06DashboardData } from "@/lib/i06/dashboard-data";

export default function Page() {
  return (
    <AppShell currentPath="/alertas-operativas">
      <section className="hero">
        <div className="kicker">capa i06</div>
        <h1 style={{ margin: 0 }}>Alertas operativas</h1>
        <div className="subtle">Excepciones visibles para que el panel no sea puro escaparate bonito.</div>
      </section>
      <SectionCard title="Semáforo rápido" subtitle="Lectura de incidentes críticos.">
        <div className="list">
          <div className="list-item">Quiebres visibles: {pcI06DashboardData.alerts.stockoutCount}</div>
          <div className="list-item">Sobreinventario visible: {pcI06DashboardData.alerts.overstockCount}</div>
          <div className="list-item">Outbox fallido: {pcI06DashboardData.alerts.failedOutbox}</div>
          <div className="list-item">Outbox pendiente: {pcI06DashboardData.alerts.pendingOutbox}</div>
          <div className="list-item">Recibos con incidencia: {pcI06DashboardData.alerts.incidentReceipts}</div>
        </div>
      </SectionCard>
      <SectionCard title="Quiebres con más filo" subtitle="Muestra corta para seguimiento diario.">
        <div className="list">
          {pcI06DashboardData.stockouts.slice(0, 8).map((item) => (
            <div key={`${item.sku}-${item.location}`} className="list-item">{item.sku} · {item.location} · disponible {item.available} · cobertura {item.daysCover} días</div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
