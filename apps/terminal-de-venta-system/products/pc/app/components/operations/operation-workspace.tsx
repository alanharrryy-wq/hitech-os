import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import type { OperationWorkspace as OperationWorkspaceModel } from "@/modules/operations/types";

function money(cents: number | null) {
  if (cents === null || Number.isNaN(cents)) return "sin datos";
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function currentPath(mode: OperationWorkspaceModel["mode"]) {
  if (mode === "purchasing") return "/purchasing";
  if (mode === "receiving") return "/receiving";
  if (mode === "replenishment") return "/replenishment";
  return "/dashboard";
}

export function OperationWorkspace({ workspace, currentPath: selectedPath }: { workspace: OperationWorkspaceModel; currentPath?: string }) {
  const showPurchasing = workspace.mode === "purchasing" || workspace.mode === "dashboard";
  const showReceiving = workspace.mode === "receiving" || workspace.mode === "dashboard";
  const showReplenishment = workspace.mode === "replenishment" || workspace.mode === "dashboard";
  const showKpis = workspace.mode === "dashboard";

  return (
    <AppShell currentPath={selectedPath ?? currentPath(workspace.mode)}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{workspace.kicker}</div>
            <h1 className="hero-title">{workspace.title}</h1>
            <p>{workspace.description}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Estado: {workspace.meta.persistence === "available" ? "información disponible" : "información no disponible"}</span>
            <span className="chip">Actualizado: {workspace.meta.generatedAt}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">Órdenes: {workspace.summary.openOrders}</span>
          <span className="alert-chip">Recepciones con diferencia: {workspace.summary.receiptsWithDiscrepancy}</span>
          <span className="alert-chip">Reabasto: {workspace.summary.replenishmentSignals}</span>
        </div>
      </section>

      {workspace.meta.warnings.length ? (
        <div className="alert-strip" role="status">
          <strong>Información temporalmente no disponible</strong>
          <span className="subtle">{workspace.meta.warnings.join(" · ")}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        <article className="card metric-card"><div className="kicker">compras</div><div className="card-title">Órdenes abiertas</div><div className="metric">{workspace.summary.openOrders}</div><div className="metric-note">Pedidos pendientes de completar.</div></article>
        <article className="card metric-card"><div className="kicker">recepción</div><div className="card-title">Con diferencia</div><div className="metric">{workspace.summary.receiptsWithDiscrepancy}</div><div className="metric-note">Recepciones que no coinciden con lo esperado.</div></article>
        <article className="card metric-card"><div className="kicker">reabasto</div><div className="card-title">Señales activas</div><div className="metric">{workspace.summary.replenishmentSignals}</div><div className="metric-note">Productos que requieren revisión de existencias.</div></article>
        <article className="card metric-card"><div className="kicker">ventas</div><div className="card-title">Venta neta</div><div className="metric">{money(workspace.summary.netSalesCents)}</div><div className="metric-note">Venta después de devoluciones registradas.</div></article>
      </section>

      {showKpis ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">indicadores</div><h2 className="section-title">Cómo se calculan los indicadores</h2><div className="section-copy">Cada indicador muestra su cálculo, periodo y estado para que puedas interpretar el resultado.</div></div></div>
          <DataTable
            columns={["Indicador", "Valor", "Cálculo", "Periodo", "Estado"]}
            rows={workspace.kpis.map((kpi) => ({ Indicador: kpi.label, Valor: kpi.value, Cálculo: kpi.formula, Periodo: kpi.range, Estado: kpi.status }))}
            emptyMessage="No hay indicadores calculables con la información disponible."
          />
        </section>
      ) : null}

      {workspace.alerts.length ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">alertas</div><h2 className="section-title">Situaciones que requieren atención</h2><div className="section-copy">Revisa la severidad, el área afectada y el detalle antes de actuar.</div></div></div>
          <DataTable
            columns={["Severidad", "Área", "Alerta", "Detalle"]}
            rows={workspace.alerts.map((alert) => ({ Severidad: alert.severity, Área: alert.module, Alerta: alert.title, Detalle: alert.detail }))}
            emptyMessage="No hay alertas críticas en la información actual."
          />
        </section>
      ) : null}

      {showPurchasing ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">compras</div><h2 className="section-title">Órdenes de compra</h2><div className="section-copy">Estado, proveedor, unidades, pendientes y riesgo.</div></div></div>
          <DataTable
            columns={["Folio", "Proveedor", "Estado", "Esperada", "Unidades", "Recibidas", "Pendientes", "Total", "Riesgo"]}
            rows={workspace.purchases.map((row) => ({ Folio: row.folio, Proveedor: row.supplier, Estado: row.status, Esperada: row.expectedAt, Unidades: row.orderedQty, Recibidas: row.receivedQty, Pendientes: row.pendingQty, Total: money(row.totalCents), Riesgo: row.risk }))}
            emptyMessage="No hay órdenes de compra para mostrar."
          />
        </section>
      ) : null}

      {showReceiving ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">recepción</div><h2 className="section-title">Recepción contra orden</h2><div className="section-copy">Compara lo esperado contra lo recibido.</div></div></div>
          <DataTable
            columns={["Folio", "Orden", "Proveedor", "Estado", "Recibida", "Esperado", "Recibido", "Diferencia", "Tipo", "Total"]}
            rows={workspace.receipts.map((row) => ({ Folio: row.folio, Orden: row.purchaseFolio, Proveedor: row.supplier, Estado: row.status, Recibida: row.receivedAt, Esperado: row.expectedQty, Recibido: row.receivedQty, Diferencia: row.discrepancyQty, Tipo: row.discrepancyLabel, Total: money(row.totalCents) }))}
            emptyMessage="No hay recepciones para comparar."
          />
        </section>
      ) : null}

      {showReplenishment ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">reabasto</div><h2 className="section-title">Señales de reabasto</h2><div className="section-copy">Prioridad, existencias actuales y cantidad sugerida.</div></div></div>
          <DataTable
            columns={["SKU", "Producto", "Ubicación", "Prioridad", "Existencias", "Mín", "Máx", "Sugerido", "Motivo"]}
            rows={workspace.replenishment.map((row) => ({ SKU: row.sku, Producto: row.name, Ubicación: row.location, Prioridad: row.priority, Existencias: row.currentStock, Mín: row.minStock, Máx: row.maxStock, Sugerido: row.suggestedQty, Motivo: row.reason }))}
            emptyMessage="No hay señales de reabasto activas."
          />
        </section>
      ) : null}

      {!workspace.purchases.length && !workspace.receipts.length && !workspace.replenishment.length && !workspace.kpis.length ? (
        <EmptyState title="Operación sin información disponible." description="No hay registros disponibles para mostrar en este momento." />
      ) : null}
    </AppShell>
  );
}
