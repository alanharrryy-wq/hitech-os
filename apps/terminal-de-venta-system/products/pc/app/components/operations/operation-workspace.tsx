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
  const resolvedPath = selectedPath ?? currentPath(workspace.mode);
  const wave2Suppliers = resolvedPath === "/proveedores";
  const showPurchasing = workspace.mode === "purchasing" || workspace.mode === "dashboard";
  const showReceiving = workspace.mode === "receiving" || workspace.mode === "dashboard";
  const showReplenishment = workspace.mode === "replenishment" || workspace.mode === "dashboard";
  const showKpis = workspace.mode === "dashboard";

  return (
    <AppShell currentPath={resolvedPath}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{workspace.kicker}</div>
            <h1 className="hero-title">{workspace.title}</h1>
            <p>{workspace.description}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Estado: {workspace.meta.persistence === "available" ? (wave2Suppliers ? "información disponible" : "datos disponibles") : (wave2Suppliers ? "información no disponible" : "sin datos disponibles")}</span>
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
        <div className="alert-strip" role={wave2Suppliers ? "status" : undefined}>
          <strong>{wave2Suppliers ? "Información temporalmente no disponible" : "Limitación visible"}</strong>
          <span className="subtle">{workspace.meta.warnings.join(" · ")}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        <article className="card metric-card"><div className="kicker">compras</div><div className="card-title">Órdenes abiertas</div><div className="metric">{workspace.summary.openOrders}</div><div className="metric-note">{wave2Suppliers ? "Pedidos pendientes de completar." : "Pendientes reales desde PurchaseOrder."}</div></article>
        <article className="card metric-card"><div className="kicker">recepción</div><div className="card-title">Con diferencia</div><div className="metric">{workspace.summary.receiptsWithDiscrepancy}</div><div className="metric-note">{wave2Suppliers ? "Recepciones que no coinciden con lo esperado." : "Recepciones contra orden."}</div></article>
        <article className="card metric-card"><div className="kicker">reabasto</div><div className="card-title">Señales activas</div><div className="metric">{workspace.summary.replenishmentSignals}</div><div className="metric-note">{wave2Suppliers ? "Productos que requieren revisión de existencias." : "Prioridad y sugeridos."}</div></article>
        <article className="card metric-card"><div className="kicker">ventas</div><div className="card-title">Venta neta</div><div className="metric">{money(workspace.summary.netSalesCents)}</div><div className="metric-note">{wave2Suppliers ? "Venta después de devoluciones registradas." : "Fórmula visible en KPI."}</div></article>
      </section>

      {showKpis ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">{wave2Suppliers ? "indicadores" : "KPI formal"}</div><h2 className="section-title">{wave2Suppliers ? "Cómo se calculan los indicadores" : "Fórmula, fuente, confianza y rango"}</h2><div className="section-copy">{wave2Suppliers ? "Cada indicador muestra su cálculo, periodo y estado para que puedas interpretar el resultado." : "Cada KPI dice de dónde sale y qué tanto se puede confiar. Nada de NaN con sombrero."}</div></div></div>
          <DataTable
            columns={wave2Suppliers ? ["Indicador", "Valor", "Cálculo", "Periodo", "Estado"] : ["KPI", "Valor", "Fórmula", "Rango", "Estado"]}
            rows={workspace.kpis.map((kpi) => wave2Suppliers
              ? ({ Indicador: kpi.label, Valor: kpi.value, Cálculo: kpi.formula, Periodo: kpi.range, Estado: kpi.status })
              : ({ KPI: kpi.label, Valor: kpi.value, Fórmula: kpi.formula, Rango: kpi.range, Estado: kpi.status }))}
            emptyMessage={wave2Suppliers ? "No hay indicadores calculables con la información disponible." : "No hay KPIs calculables porque la persistencia no está disponible."}
          />
        </section>
      ) : null}

      {workspace.alerts.length ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">{wave2Suppliers ? "alertas" : "alertas accionables"}</div><h2 className="section-title">{wave2Suppliers ? "Situaciones que requieren atención" : "Focos rojos de operación"}</h2><div className="section-copy">{wave2Suppliers ? "Revisa la severidad, el área afectada y el detalle antes de actuar." : "Alertas con módulo, severidad y ruta; no chisme con icono rojo."}</div></div></div>
          <DataTable
            columns={wave2Suppliers ? ["Severidad", "Área", "Alerta", "Detalle"] : ["Severidad", "Módulo", "Alerta", "Detalle", "Ruta"]}
            rows={workspace.alerts.map((alert) => wave2Suppliers
              ? ({ Severidad: alert.severity, Área: alert.module, Alerta: alert.title, Detalle: alert.detail })
              : ({ Severidad: alert.severity, Módulo: alert.module, Alerta: alert.title, Detalle: alert.detail, Ruta: alert.href }))}
            emptyMessage={wave2Suppliers ? "No hay alertas críticas en la información actual." : "Sin alertas críticas en la muestra actual."}
          />
        </section>
      ) : null}

      {showPurchasing ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">compras</div><h2 className="section-title">Órdenes de compra</h2><div className="section-copy">Estado, proveedor, unidades, pendientes y riesgo.</div></div></div>
          <DataTable
            columns={["Folio", "Proveedor", "Estado", "Esperada", "Unidades", "Recibidas", "Pendientes", "Total", "Riesgo"]}
            rows={workspace.purchases.map((row) => ({ Folio: row.folio, Proveedor: row.supplier, Estado: row.status, Esperada: row.expectedAt, Unidades: row.orderedQty, Recibidas: row.receivedQty, Pendientes: row.pendingQty, Total: money(row.totalCents), Riesgo: row.risk }))}
            emptyMessage={wave2Suppliers ? "No hay órdenes de compra para mostrar." : "No hay órdenes de compra en persistencia canónica."}
          />
        </section>
      ) : null}

      {showReceiving ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">recepción</div><h2 className="section-title">Recepción contra orden</h2><div className="section-copy">{wave2Suppliers ? "Compara lo esperado contra lo recibido." : "Diferencias netas entre lo esperado y recibido."}</div></div></div>
          <DataTable
            columns={["Folio", "Orden", "Proveedor", "Estado", "Recibida", "Esperado", "Recibido", "Diferencia", "Tipo", "Total"]}
            rows={workspace.receipts.map((row) => ({ Folio: row.folio, Orden: row.purchaseFolio, Proveedor: row.supplier, Estado: row.status, Recibida: row.receivedAt, Esperado: row.expectedQty, Recibido: row.receivedQty, Diferencia: row.discrepancyQty, Tipo: row.discrepancyLabel, Total: money(row.totalCents) }))}
            emptyMessage={wave2Suppliers ? "No hay recepciones para comparar." : "No hay recepciones canónicas para comparar."}
          />
        </section>
      ) : null}

      {showReplenishment ? (
        <section className="card">
          <div className="section-head"><div><div className="kicker">reabasto</div><h2 className="section-title">Señales de reabasto</h2><div className="section-copy">{wave2Suppliers ? "Prioridad, existencias actuales y cantidad sugerida." : "Prioridad, stock actual, min/max y sugerido."}</div></div></div>
          <DataTable
            columns={["SKU", "Producto", "Ubicación", "Prioridad", "Existencias", "Mín", "Máx", "Sugerido", "Motivo"]}
            rows={workspace.replenishment.map((row) => ({ SKU: row.sku, Producto: row.name, Ubicación: row.location, Prioridad: row.priority, Existencias: row.currentStock, Mín: row.minStock, Máx: row.maxStock, Sugerido: row.suggestedQty, Motivo: row.reason }))}
            emptyMessage="No hay señales de reabasto activas."
          />
        </section>
      ) : null}

      {!workspace.purchases.length && !workspace.receipts.length && !workspace.replenishment.length && !workspace.kpis.length ? (
        <EmptyState
          title={wave2Suppliers ? "Operación sin información disponible." : "Operación sin datos disponibles."}
          description={wave2Suppliers ? "No hay registros disponibles para mostrar en este momento." : "La pantalla queda lista y honesta, sin inventar compras, recepciones ni KPIs."}
        />
      ) : null}
    </AppShell>
  );
}
