import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "./data-table";
import { EmptyState } from "./empty-state";
import { IngestEventPanel } from "./ingest-event-panel";
import { KpiCard } from "./kpi-card";
import type { BackofficeDashboard } from "@/lib/backoffice/dashboard";

export function ExecutiveDashboard({ dashboard, currentPath }: { dashboard: BackofficeDashboard; currentPath: string }) {
  return (
    <AppShell currentPath={currentPath}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">torre de control PC</div>
            <h1 className="hero-title">Backoffice de sincronización y gobierno</h1>
            <p>Dashboard de control: ventas consolidadas, eventos, conflictos, stock y auditoría sin bloquear la venta local de Tablet.</p>
          </div>
          <div className="inline-list">
            <span className="chip">Tablet POS local</span>
            <span className="chip">PC backoffice</span>
            <span className="chip">{dashboard.sync.healthLabel}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">/pos es el POS operativo</span>
          <span className="alert-chip">/prisma-dark-pos-reference es referencia visual</span>
          <span className="alert-chip">lastIngestAt: {dashboard.sync.lastIngestAt ?? "no disponible"}</span>
        </div>
      </section>

      {dashboard.meta.warnings.length ? (
        <div className="alert-strip">
          <strong>{dashboard.meta.warnings[0]}</strong>
          <span className="subtle">Persistencia: {dashboard.meta.persistence}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        {dashboard.kpis.map((kpi) => (
          <KpiCard key={kpi.key} kpi={kpi} />
        ))}
      </section>

      <section className="grid cols-2">
        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">ventas reales</div>
              <h2 className="section-title">Top SKUs del día</h2>
              <div className="section-copy">Calculado desde líneas de venta canónicas cuando existen datos reales.</div>
            </div>
          </div>
          <DataTable
            columns={["SKU", "Producto", "Unidades", "Ingreso"]}
            rows={dashboard.topSkus.map((row) => ({
              SKU: row.sku,
              Producto: row.productName,
              Unidades: row.qty,
              Ingreso: new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(row.totalCents / 100)
            }))}
            emptyMessage="No hay SKUs vendidos consolidados para el día."
          />
        </article>

        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">sync visible</div>
              <h2 className="section-title">Estado de sincronización</h2>
              <div className="section-copy">El tablero distingue validación de eventos de persistencia de ingest consolidado.</div>
            </div>
          </div>
          <div className="list">
            <div className="list-item">
              <span>Eventos pendientes</span>
              <strong>{dashboard.sync.pendingEvents}</strong>
            </div>
            <div className="list-item">
              <span>Eventos fallidos</span>
              <strong>{dashboard.sync.failedEvents}</strong>
            </div>
            <div className="list-item">
              <span>Conflictos visibles</span>
              <strong>{dashboard.sync.conflictCount}</strong>
            </div>
            <div className="list-item">
              <span>Último evento outbox</span>
              <strong>{dashboard.sync.lastOutboxEventAt ?? "no disponible"}</strong>
            </div>
          </div>
          {!dashboard.meta.hasConsolidatedEvents ? <EmptyState title="Aún no hay eventos consolidados." description="La UI queda lista sin inventar KPIs productivos." /> : null}
        </article>
      </section>

      <IngestEventPanel />
    </AppShell>
  );
}
