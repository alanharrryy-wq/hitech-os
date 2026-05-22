import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import type { CommandCenterModel, CommandMetric, CommandPanel } from "@/server/services/pc-command-center.service";
import { PcCommandActions } from "./pc-command-actions";

function toneClass(tone?: CommandMetric["tone"]) {
  if (tone === "danger") return "tone-danger";
  if (tone === "warn") return "tone-warn";
  return "tone-ok";
}

function MetricCard({ metric }: { metric: CommandMetric }) {
  return (
    <article className="card metric-card">
      <div className="kicker">{metric.label}</div>
      <div className="metric">{metric.value}</div>
      <div className="metric-note">{metric.note}</div>
      <span className={`status-pill ${toneClass(metric.tone)}`}>{metric.tone === "danger" ? "critico" : metric.tone === "warn" ? "revisar" : "ok"}</span>
    </article>
  );
}

function Panel({ panel }: { panel: CommandPanel }) {
  return (
    <div className="alert-strip">
      <strong>{panel.title}</strong>
      <span className="subtle">{panel.body}</span>
    </div>
  );
}

export function PcCommandCenterPage({ model }: { model: CommandCenterModel }) {
  return (
    <AppShell currentPath={model.currentPath}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{model.kicker}</div>
            <h1 className="hero-title">{model.title}</h1>
            <p>{model.description}</p>
          </div>
          <div className="inline-list">
            <span className="chip">PC gobierna</span>
            <span className="chip">Tablet opera independiente</span>
            {model.periodLabel ? <span className="chip">{model.periodLabel}</span> : null}
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">{model.sourceLine}</span>
          <span className="alert-chip">{model.independenceLine}</span>
        </div>
      </section>

      {model.actions?.length ? (
        <section className="card">
          <div className="section-head">
            <div>
              <div className="kicker">acciones</div>
              <h2 className="section-title">Zona de accion</h2>
              <p className="section-copy">Solo se muestran acciones con ruta real o razon de bloqueo.</p>
            </div>
          </div>
          <PcCommandActions actions={model.actions} />
        </section>
      ) : null}

      <section className="dashboard-grid">
        {model.metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}
      </section>

      {model.panels.length ? (
        <section className="grid">
          {model.panels.map((panel) => <Panel key={panel.title} panel={panel} />)}
        </section>
      ) : null}

      {model.tables.length ? model.tables.map((table) => (
        <section className="card" key={table.title}>
          <div className="section-head">
            <div>
              <div className="kicker">{table.caption}</div>
              <h2 className="section-title">{table.title}</h2>
            </div>
          </div>
          <DataTable columns={table.columns} rows={table.rows} emptyMessage={table.emptyMessage} />
        </section>
      )) : (
        <EmptyState title="Sin datos disponibles." description="La pantalla queda honesta: no usa datos fake ni estados de exito inventados." />
      )}

      <section className="card">
        <details>
          <summary>Diagnostico admin sanitizado</summary>
          <pre>{JSON.stringify(model.diagnostics, null, 2)}</pre>
        </details>
      </section>
    </AppShell>
  );
}
