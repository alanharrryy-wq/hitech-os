import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { StatusBadge } from "@components/backoffice/status-badge";
import type { InventoryWorkspace, InventoryWorkspaceView } from "@/modules/inventory/types";

function qty(value: number) {
  return new Intl.NumberFormat("es-MX", { maximumFractionDigits: 0 }).format(value);
}

function pct(value: number | null) {
  if (value === null) return "sin base";
  return `${new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 }).format(value * 100)}%`;
}

function currentPath(view: InventoryWorkspaceView) {
  if (view === "counts") return "/counts";
  if (view === "audit") return "/audit";
  return "/stock";
}

function titleFor(view: InventoryWorkspaceView) {
  if (view === "counts") return "Conteos físicos y exactitud";
  if (view === "audit") return "Auditoría de inventario";
  return "Existencias y movimientos";
}

function copyFor(view: InventoryWorkspaceView) {
  if (view === "counts") return "Diferencias, exactitud y conteos pendientes para cerrar inventario sin rezarle a la libreta.";
  if (view === "audit") return "Bitácora explicable de acciones sensibles, riesgos de integridad y evidencia operativa.";
  return "Stock actual, ledger derivado y movimientos recientes con antes/después calculado cuando la base lo permite.";
}

export function InventoryWorkspaceView({ view, workspace }: { view: InventoryWorkspaceView; workspace: InventoryWorkspace }) {
  const path = currentPath(view);
  return (
    <AppShell currentPath={path}>
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">inventario auditable</div>
            <h1 className="hero-title">{titleFor(view)}</h1>
            <p>{copyFor(view)}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Fuente: {workspace.meta.source}</span>
            <span className="chip">Confianza: {workspace.meta.confidence}</span>
            <span className="chip">Actualizado: {workspace.meta.generatedAt}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">Stock visible</span>
          <span className="alert-chip">Movimientos trazables</span>
          <span className="alert-chip">Conteos con diferencia</span>
          <span className="alert-chip">Riesgos auditables</span>
        </div>
      </section>

      {workspace.meta.warnings.length ? (
        <div className="alert-strip">
          <strong>Limitación visible</strong>
          <span className="subtle">{workspace.meta.warnings.join(" · ")}</span>
        </div>
      ) : null}

      <section className="dashboard-grid">
        <article className="card metric-card">
          <div className="kicker">existencias</div>
          <div className="card-title">SKUs con snapshot</div>
          <div className="metric">{workspace.summary.stockedSkuCount}</div>
          <div className="metric-note">Productos con foto de inventario por ubicación.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">riesgo</div>
          <div className="card-title">Stock crítico</div>
          <div className="metric">{workspace.summary.criticalStockCount}</div>
          <div className="metric-note">Cero, negativo o cobertura menor a dos días.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">conteos</div>
          <div className="card-title">Exactitud</div>
          <div className="metric">{pct(workspace.summary.inventoryAccuracy)}</div>
          <div className="metric-note">Conteos sin variación sobre conteos totales.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">auditoría</div>
          <div className="card-title">Hallazgos</div>
          <div className="metric">{workspace.auditFindings.length}</div>
          <div className="metric-note">Riesgos accionables detectados por integridad.</div>
        </article>
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">filtros</div>
            <h2 className="section-title">Búsqueda operativa</h2>
            <div className="section-copy">Filtra por producto, ubicación, estado, estatus de conteo o severidad.</div>
          </div>
        </div>
        <form className="dashboard-actions" action={path}>
          <label className="action-card">
            <strong>Buscar</strong>
            <input name="q" defaultValue={workspace.filters.q} placeholder="SKU, producto, motivo o ubicación" />
          </label>
          {view === "stock" ? (
            <label className="action-card">
              <strong>Estado</strong>
              <select name="state" defaultValue={workspace.filters.state}>
                <option value="all">Todos</option>
                <option value="critical">Crítico</option>
                <option value="low">Bajo</option>
                <option value="ok">OK</option>
              </select>
            </label>
          ) : null}
          {view === "counts" ? (
            <label className="action-card">
              <strong>Estatus</strong>
              <select name="status" defaultValue={workspace.filters.countStatus}>
                <option value="all">Todos</option>
                <option value="open">Abierto</option>
                <option value="review">Revisión</option>
                <option value="closed">Cerrado</option>
              </select>
            </label>
          ) : null}
          {view === "audit" ? (
            <label className="action-card">
              <strong>Severidad</strong>
              <select name="severity" defaultValue={workspace.filters.auditSeverity}>
                <option value="all">Todas</option>
                <option value="CRÍTICO">Crítico</option>
                <option value="ALTO">Alto</option>
                <option value="MEDIO">Medio</option>
              </select>
            </label>
          ) : null}
          <label className="action-card">
            <strong>Ubicación</strong>
            <select name="location" defaultValue={workspace.filters.location}>
              <option value="all">Todas</option>
              {workspace.locations.map((location) => <option key={location} value={location}>{location}</option>)}
            </select>
          </label>
          <button type="submit">Aplicar filtros</button>
          <a className="footer-chip" href={path}>Limpiar</a>
        </form>
      </section>

      {view === "stock" ? <StockPanel workspace={workspace} /> : null}
      {view === "counts" ? <CountsPanel workspace={workspace} /> : null}
      {view === "audit" ? <AuditPanel workspace={workspace} /> : null}

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">estado honesto</div>
            <h2 className="section-title">Notas de implementación I03</h2>
          </div>
        </div>
        <div className="list">
          <div className="list-item"><span>Alcance</span><strong>Stock, conteos, ledger derivado y auditoría operativa.</strong></div>
          <div className="list-item"><span>No toca</span><strong>Tablet, shared-kernel, sync compartido ni schema Prisma.</strong></div>
          <div className="list-item"><span>Persistencia</span><strong>{workspace.meta.persistence}</strong></div>
          <div className="list-item"><span>Ledger</span><strong>{workspace.meta.ledgerMode}</strong></div>
        </div>
      </section>
    </AppShell>
  );
}

function StockPanel({ workspace }: { workspace: InventoryWorkspace }) {
  return (
    <section className="grid cols-2">
      <article className="card">
        <div className="section-head"><div><div className="kicker">stock</div><h2 className="section-title">Existencias por ubicación</h2></div></div>
        <DataTable
          columns={["SKU", "Producto", "Ubicación", "Disponible", "Reservado", "Cobertura", "Estado"]}
          rows={workspace.snapshots.map((row) => ({
            SKU: row.sku,
            Producto: row.productName,
            Ubicación: row.location,
            Disponible: qty(row.available),
            Reservado: qty(row.reserved),
            Cobertura: row.daysCoverLabel,
            Estado: row.stateLabel
          }))}
          emptyMessage="No hay snapshots para los filtros seleccionados."
        />
      </article>
      <article className="card">
        <div className="section-head"><div><div className="kicker">ledger</div><h2 className="section-title">Movimientos recientes</h2></div></div>
        <DataTable
          columns={["Fecha", "SKU", "Movimiento", "Cantidad", "Antes", "Después", "Motivo", "Origen"]}
          rows={workspace.ledger.map((row) => ({
            Fecha: row.createdAtLabel,
            SKU: row.sku,
            Movimiento: row.movement,
            Cantidad: qty(row.quantityDelta),
            Antes: row.beforeQty === null ? "derivado" : qty(row.beforeQty),
            Después: row.afterQty === null ? "derivado" : qty(row.afterQty),
            Motivo: row.reason,
            Origen: row.source
          }))}
          emptyMessage="No hay movimientos trazables para los filtros seleccionados."
        />
      </article>
    </section>
  );
}

function CountsPanel({ workspace }: { workspace: InventoryWorkspace }) {
  return (
    <section className="grid cols-2">
      <article className="card">
        <div className="section-head"><div><div className="kicker">conteos</div><h2 className="section-title">Conteos físicos</h2></div></div>
        <DataTable
          columns={["Fecha", "Ubicación", "Contó", "Variación", "Exactitud", "Estado"]}
          rows={workspace.counts.map((row) => ({
            Fecha: row.countedAtLabel,
            Ubicación: row.location,
            Contó: row.countedBy,
            Variación: qty(row.variance),
            Exactitud: row.accuracyLabel,
            Estado: row.status
          }))}
          emptyMessage="No hay conteos para los filtros seleccionados."
        />
      </article>
      <article className="card">
        <div className="section-head"><div><div className="kicker">diferencias</div><h2 className="section-title">Riesgos por conteo</h2></div></div>
        {workspace.countFindings.length ? (
          <div className="list">
            {workspace.countFindings.map((finding) => (
              <div className="alert-strip" key={finding.id}>
                <strong>{finding.title}</strong>
                <span className="subtle">{finding.detail}</span>
                <StatusBadge value={finding.severity} />
              </div>
            ))}
          </div>
        ) : <EmptyState title="Sin diferencias críticas." description="Los conteos cargados no tienen hallazgos graves para los filtros actuales." />}
      </article>
    </section>
  );
}

function AuditPanel({ workspace }: { workspace: InventoryWorkspace }) {
  return (
    <section className="grid cols-2">
      <article className="card">
        <div className="section-head"><div><div className="kicker">auditoría</div><h2 className="section-title">Hallazgos de integridad</h2></div></div>
        <DataTable
          columns={["Severidad", "Tipo", "Entidad", "Detalle", "Acción"]}
          rows={workspace.auditFindings.map((finding) => ({
            Severidad: finding.severity,
            Tipo: finding.type,
            Entidad: finding.entityLabel,
            Detalle: finding.detail,
            Acción: finding.recommendedAction
          }))}
          emptyMessage="No hay hallazgos de auditoría para los filtros seleccionados."
        />
      </article>
      <article className="card">
        <div className="section-head"><div><div className="kicker">acciones sensibles</div><h2 className="section-title">Movimientos auditables</h2></div></div>
        <DataTable
          columns={["Fecha", "SKU", "Actor", "Motivo", "Origen", "Antes", "Después"]}
          rows={workspace.ledger.slice(0, 20).map((row) => ({
            Fecha: row.createdAtLabel,
            SKU: row.sku,
            Actor: row.actor,
            Motivo: row.reason,
            Origen: row.source,
            Antes: row.beforeQty === null ? "derivado" : qty(row.beforeQty),
            Después: row.afterQty === null ? "derivado" : qty(row.afterQty)
          }))}
          emptyMessage="No hay movimientos auditables disponibles."
        />
      </article>
    </section>
  );
}
