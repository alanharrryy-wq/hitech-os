import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { PcSyncChartPromotionPanel } from "@components/sync/pc-sync-chart-promotion-panel";
import type { CommandCenterModel, CommandMetric, CommandPanel, CommandTable, CommandTableRow } from "@/server/services/pc-command-center.service";
import { PcCommandActions } from "./pc-command-actions";
import { SalesControlBranchView } from "./sales-control-branch-view";
import { CashSessionsOperationalView } from "./cash-sessions-operational-view";

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

function humanSurface(value: unknown) {
  const raw = String(value ?? "").toLowerCase();
  if (raw.includes("tablet")) return "Tablet";
  if (raw.includes("mobile")) return "Mobile";
  if (raw.includes("pc")) return "PC";
  return raw ? "Equipo" : "No disponible";
}

function customerText(value: string) {
  return value
    .replace(/Prisma Original Customer/gi, "tu negocio")
    .replace(/lifecycle/gi, "resultado")
    .replace(/checkpoint/gi, "avance")
    .replace(/outbox/gi, "pendientes")
    .replace(/heartbeat/gi, "conexión")
    .replace(/payload/gi, "detalle")
    .replace(/canonical/gi, "principal")
    .replace(/canonico/gi, "principal")
    .replace(/canónico/gi, "principal");
}

function customerCell(value: CommandTableRow[string]): CommandTableRow[string] {
  if (typeof value === "string") return customerText(value);
  if (Array.isArray(value)) return value.map((item) => customerText(item));
  return value;
}

function wave2CustomerTable(path: string, table: CommandTable): CommandTable {
  const hidden = path === "/devices"
    ? new Set(["Fuente", "Modo", "Dispositivo", "ID", "Id", "Código"])
    : new Set(["Fuente", "Evento", "Agregado", "Dispositivo", "Terminal", "Código", "ID", "Id", "Topic", "Tópico"]);
  const columns = table.columns.filter((column) => !hidden.has(column));
  const rows = table.rows.map((row) => {
    const projected: CommandTableRow = {};
    for (const column of columns) {
      const value = row[column];
      if (column === "Superficie") {
        projected[column] = humanSurface(value);
      } else {
        projected[column] = customerCell(value);
      }
    }
    const href = typeof row.__rowActionHref === "string" && !row.__rowActionHref.startsWith("/api/") ? row.__rowActionHref : undefined;
    if (href) {
      projected.__rowActionHref = href;
      projected.__rowActionLabel = customerText(row.__rowActionLabel || "Abrir detalle");
    }
    return projected;
  });
  return {
    ...table,
    title: customerText(table.title),
    caption: customerText(table.caption),
    columns,
    rows,
    emptyMessage: customerText(table.emptyMessage)
  };
}

export function PcCommandCenterPage({ model }: { model: CommandCenterModel }) {
  if (model.currentPath === "/sales-control" && model.salesControl) {
    return <SalesControlBranchView model={model} />;
  }

  if (model.currentPath === "/cash-sessions" || model.mode === "cash") {
    return <CashSessionsOperationalView model={model} />;
  }

  const wave2CustomerSurface = model.currentPath === "/sync" || model.currentPath === "/devices";
  const visibleTitle = wave2CustomerSurface ? customerText(model.title) : model.title;
  const visibleDescription = wave2CustomerSurface ? customerText(model.description) : model.description;
  const visibleMetrics = wave2CustomerSurface
    ? model.metrics.map((metric) => ({
        ...metric,
        label: customerText(metric.label),
        value: customerText(metric.value),
        note: customerText(metric.note)
      }))
    : model.metrics;
  const visiblePanels = wave2CustomerSurface
    ? model.panels.map((panel) => ({ ...panel, title: customerText(panel.title), body: customerText(panel.body) }))
    : model.panels;
  const visibleActions = wave2CustomerSurface
    ? (model.actions ?? [])
        .filter((action) => action.method === "POST" || !action.href.startsWith("/api/"))
        .map((action) => ({
          ...action,
          label: customerText(action.label),
          disabledReason: action.disabledReason ? customerText(action.disabledReason) : undefined,
          successMessage: action.successMessage ? customerText(action.successMessage) : undefined
        }))
    : (model.actions ?? []);
  const visibleTables = wave2CustomerSurface
    ? model.tables.map((table) => wave2CustomerTable(model.currentPath, table))
    : model.tables;

  return (
    <AppShell currentPath={model.currentPath}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{model.kicker}</div>
            <h1 className="hero-title">{visibleTitle}</h1>
            <p>{visibleDescription}</p>
          </div>
          <div className="inline-list">
            {wave2CustomerSurface ? null : <span className="chip">PC gobierna</span>}
            {wave2CustomerSurface ? null : <span className="chip">Tablet opera independiente</span>}
            {model.periodLabel ? <span className="chip">{model.periodLabel}</span> : null}
          </div>
        </div>
        {wave2CustomerSurface ? null : (
          <div className="hero-badges">
            <span className="alert-chip">{model.sourceLine}</span>
            <span className="alert-chip">{model.independenceLine}</span>
          </div>
        )}
      </section>

      {visibleActions.length ? (
        <section className="card">
          <div className="section-head">
            <div>
              <div className="kicker">acciones</div>
              <h2 className="section-title">{wave2CustomerSurface ? "Acciones disponibles" : "Zona de accion"}</h2>
              <p className="section-copy">{wave2CustomerSurface ? "Las acciones disponibles muestran su resultado; las restringidas explican por qué no pueden ejecutarse." : "Solo se muestran acciones con ruta real o razon de bloqueo."}</p>
            </div>
          </div>
          <PcCommandActions actions={visibleActions} customerSafe={wave2CustomerSurface} />
        </section>
      ) : null}

      <section className="dashboard-grid">
        {visibleMetrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)}
      </section>

      {visiblePanels.length ? (
        <section className="grid">
          {visiblePanels.map((panel) => <Panel key={panel.title} panel={panel} />)}
        </section>
      ) : null}

      {model.mode === "sync" ? <PcSyncChartPromotionPanel /> : null}

      {visibleTables.length ? visibleTables.map((table) => (
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
        <EmptyState title="Sin datos disponibles." description={wave2CustomerSurface ? "No hay información disponible para mostrar en este momento." : "La pantalla queda honesta: no usa datos fake ni estados de exito inventados."} />
      )}
    </AppShell>
  );
}
