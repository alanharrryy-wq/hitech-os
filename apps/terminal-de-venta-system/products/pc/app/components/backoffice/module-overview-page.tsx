import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "./data-table";
import { EmptyState } from "./empty-state";
import type { BackofficeModuleOverview } from "@/lib/backoffice/overview";
import type { ReactNode } from "react";

export function ModuleOverviewPage({ overview, children }: { overview: BackofficeModuleOverview; children?: ReactNode }) {
  return (
    <AppShell currentPath={overview.route}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{overview.eyebrow}</div>
            <h1 className="hero-title">{overview.title}</h1>
            <p>{overview.description}</p>
          </div>
          <div className="inline-list">
            <span className="chip">PC backoffice</span>
            <span className="chip">Persistencia: {overview.meta.persistence}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">Tablet vende local</span>
          <span className="alert-chip">Eventos son verdad operacional</span>
          <span className="alert-chip">Sin datos falsos</span>
        </div>
      </section>

      {overview.meta.warnings.length ? (
        <div className="alert-strip">
          <strong>Limitación visible</strong>
          <span className="subtle">{overview.meta.warnings[0]}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        {overview.metrics.map((metric) => (
          <article key={metric.label} className="card metric-card">
            <div className="kicker">indicador</div>
            <div className="card-title">{metric.label}</div>
            <div className="metric">{metric.value}</div>
            <div className="metric-note">{metric.note}</div>
          </article>
        ))}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">vista consolidada</div>
            <h2 className="section-title">{overview.table.title}</h2>
            <div className="section-copy">Lectura de backoffice; no ejecuta venta ni condiciona el POS Tablet.</div>
          </div>
        </div>
        {overview.table.columns.length ? (
          <DataTable columns={overview.table.columns} rows={overview.table.rows} emptyMessage={overview.table.emptyMessage} />
        ) : (
          <EmptyState title="Aún no hay eventos consolidados." description={overview.table.emptyMessage} />
        )}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">estado honesto</div>
            <h2 className="section-title">Notas de alcance</h2>
          </div>
        </div>
        <div className="list">
          {overview.notes.map((note) => (
            <div key={note} className="list-item">
              <span>{note}</span>
            </div>
          ))}
        </div>
      </section>
      {children}
    </AppShell>
  );
}
