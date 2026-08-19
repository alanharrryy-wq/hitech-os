import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "./data-table";
import { EmptyState } from "./empty-state";
import type { BackofficeModuleOverview } from "@/lib/backoffice/overview";
import type { ReactNode } from "react";

function persistenceLabel(value: BackofficeModuleOverview["meta"]["persistence"]) {
  if (value === "available") return "disponible";
  if (value === "unavailable") return "no disponible";
  return "no requerida";
}

function settingsMetricNote(note: string) {
  return note
    .replace(/ canónicos?/gi, "")
    .replace(/ persistidos?/gi, "")
    .replace(/ para el negocio/gi, "")
    .replace(/ disponibles\.?$/i, ".");
}

export function ModuleOverviewPage({ overview, children }: { overview: BackofficeModuleOverview; children?: ReactNode }) {
  const wave2Settings = overview.route === "/settings";
  const tableTitle = wave2Settings ? "Usuarios y roles" : overview.table.title;
  const emptyMessage = wave2Settings ? "No hay usuarios registrados para mostrar." : overview.table.emptyMessage;
  const notes = wave2Settings
    ? ["Los cambios de permisos deben realizarse desde acciones autorizadas y quedar registrados para revisión."]
    : overview.notes;

  return (
    <AppShell currentPath={overview.route}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{overview.eyebrow}</div>
            <h1 className="hero-title">{overview.title}</h1>
            <p>{wave2Settings ? "Consulta usuarios, roles, permisos, tiendas y terminales configuradas." : overview.description}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Panel administrativo</span>
            <span className="chip">Información: {persistenceLabel(overview.meta.persistence)}</span>
          </div>
        </div>
      </section>

      {overview.meta.warnings.length ? (
        <div className="alert-strip" role="status">
          <strong>Información temporalmente no disponible</strong>
          <span className="subtle">{overview.meta.warnings[0]}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        {overview.metrics.map((metric) => (
          <article key={metric.label} className="card metric-card">
            <div className="kicker">indicador</div>
            <div className="card-title">{metric.label}</div>
            <div className="metric">{metric.value}</div>
            <div className="metric-note">{wave2Settings ? settingsMetricNote(metric.note) : metric.note}</div>
          </article>
        ))}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">vista consolidada</div>
            <h2 className="section-title">{tableTitle}</h2>
            <div className="section-copy">Consulta la información administrativa disponible para esta área.</div>
          </div>
        </div>
        {overview.table.columns.length ? (
          <DataTable columns={overview.table.columns} rows={overview.table.rows} emptyMessage={emptyMessage} />
        ) : (
          <EmptyState title="Aún no hay información para mostrar." description={emptyMessage} />
        )}
      </section>

      {notes.length ? (
        <section className="card">
          <div className="section-head">
            <div>
              <div className="kicker">alcance</div>
              <h2 className="section-title">Información importante</h2>
            </div>
          </div>
          <div className="list">
            {notes.map((note) => (
              <div key={note} className="list-item">
                <span>{note}</span>
              </div>
            ))}
          </div>
        </section>
      ) : null}
      {children}
    </AppShell>
  );
}
