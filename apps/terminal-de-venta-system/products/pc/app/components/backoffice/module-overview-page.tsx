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

function FrozenWave1Overview({ overview, children }: { overview: BackofficeModuleOverview; children?: ReactNode }) {
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
            <span className="chip">Panel administrativo</span>
            <span className="chip">Persistencia: {persistenceLabel(overview.meta.persistence)}</span>
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
            <div className="section-copy">Lectura administrativa; no ejecuta venta ni condiciona el POS Tablet.</div>
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

export function ModuleOverviewPage({ overview, children }: { overview: BackofficeModuleOverview; children?: ReactNode }) {
  if (overview.route !== "/settings") return <FrozenWave1Overview overview={overview}>{children}</FrozenWave1Overview>;

  const emptyMessage = "No hay usuarios registrados para mostrar.";
  const notes = ["Los cambios de permisos deben realizarse desde acciones autorizadas y quedar registrados para revisión."];

  return (
    <AppShell currentPath={overview.route}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{overview.eyebrow}</div>
            <h1 className="hero-title">{overview.title}</h1>
            <p>Consulta usuarios, roles, permisos, tiendas y terminales configuradas.</p>
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
            <div className="metric-note">{settingsMetricNote(metric.note)}</div>
          </article>
        ))}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">vista consolidada</div>
            <h2 className="section-title">Usuarios y roles</h2>
            <div className="section-copy">Consulta la información administrativa disponible para esta área.</div>
          </div>
        </div>
        {overview.table.columns.length ? (
          <DataTable columns={overview.table.columns} rows={overview.table.rows} emptyMessage={emptyMessage} />
        ) : (
          <EmptyState title="Aún no hay información para mostrar." description={emptyMessage} />
        )}
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">alcance</div>
            <h2 className="section-title">Información importante</h2>
          </div>
        </div>
        <div className="list">
          {notes.map((note) => (
            <div key={note} className="list-item"><span>{note}</span></div>
          ))}
        </div>
      </section>
      {children}
    </AppShell>
  );
}
