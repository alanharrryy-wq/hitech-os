import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { StatusBadge } from "@components/backoffice/status-badge";
import { AppShell } from "@components/layout/app-shell";
import type { InventoryWorkspace, InventoryWorkspaceView as InventoryWorkspaceViewName, StockSnapshotView } from "@/modules/inventory/types";
import styles from "./pc-inventory-master-detail.module.css";

function qty(value: number) {
  return new Intl.NumberFormat("es-MX", { maximumFractionDigits: 0 }).format(value);
}

function pct(value: number | null) {
  if (value === null) return "sin base";
  return `${new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 }).format(value * 100)}%`;
}

function currentPath(view: InventoryWorkspaceViewName, override?: string) {
  if (override) return override;
  if (view === "counts") return "/counts";
  if (view === "audit") return "/auditoria-inventario";
  return "/stock";
}

function titleFor(view: InventoryWorkspaceViewName) {
  if (view === "counts") return "Conteo físico";
  if (view === "audit") return "Auditoría de inventario";
  return "Stock físico";
}

function copyFor(view: InventoryWorkspaceViewName) {
  if (view === "counts") return "Revisa conteos, variaciones y evidencia para cerrar diferencias con un motivo claro.";
  if (view === "audit") return "Consulta quién movió inventario, cuándo ocurrió, qué cambió y por qué.";
  return "Consulta existencias por producto y ubicación, detecta faltantes o sobrantes y revisa las acciones disponibles.";
}

function queryHref(path: string, params: Record<string, string>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value !== "all") query.set(key, value);
  });
  const text = query.toString();
  return text ? `${path}?${text}` : path;
}

function firstSnapshot(workspace: InventoryWorkspace) {
  return workspace.snapshots[0] ?? null;
}

function snapshotTone(row: StockSnapshotView) {
  if (row.state === "critical") return "danger" as const;
  if (row.state === "low") return "warn" as const;
  return "ok" as const;
}

function uniqueLocations(workspace: InventoryWorkspace) {
  return Array.from(new Set(workspace.snapshots.map((row) => row.location).filter(Boolean))).slice(0, 8);
}

function StockFicha({ snapshot }: { snapshot: StockSnapshotView | null }) {
  if (!snapshot) {
    return (
      <section
        className={styles.productFicha}
        data-pcinv-product-ficha="stock-empty"
        data-prisma-surface="pc"
        data-prisma-route="/stock"
        data-prisma-owner="StockFicha"
        data-prisma-region="ZONE.pc.stock.detail"
        data-prisma-slot="SLOT.pc.stock.detail.primary"
        data-prisma-component-ui-id="PC-STOCK-FICHA-PANEL-01"
        data-prisma-recipe="REC.panel.operational.cloudglass"
        data-prisma-visual-stack="VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
        data-prisma-binding="BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
        data-prisma-adapter="ADP.PC.DENSE.CLOUDGLASS.V1"
        data-prisma-neutral-layer="LYR.SURFACE.OPERATIONAL.DETAIL"
        data-prisma-runtime-selector="data-pcinv-product-ficha"
        data-prisma-source-owner="inventory-workspace.tsx"
        data-prisma-css-owner="pc-inventory-master-detail.module.css"
        data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1"
      >
        <div className={styles.fichaHeader}>
          <div>
            <span className={styles.kicker}>acción rápida</span>
            <h2>Sin corte seleccionado</h2>
          </div>
        </div>
        <EmptyState title="Sin existencias visibles." description="Cuando haya cortes de inventario, esta ficha mostrará ubicación, disponible, reservado, cobertura y acciones contextuales." />
      </section>
    );
  }

  return (
    <section
      className={styles.productFicha}
      data-pcinv-product-ficha="stock"
      data-prisma-surface="pc"
      data-prisma-route="/stock"
      data-prisma-owner="StockFicha"
      data-prisma-region="ZONE.pc.stock.detail"
      data-prisma-slot="SLOT.pc.stock.detail.primary"
      data-prisma-component-ui-id="PC-STOCK-FICHA-PANEL-01"
      data-prisma-recipe="REC.panel.operational.cloudglass"
      data-prisma-visual-stack="VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
      data-prisma-binding="BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
      data-prisma-adapter="ADP.PC.DENSE.CLOUDGLASS.V1"
      data-prisma-neutral-layer="LYR.SURFACE.OPERATIONAL.DETAIL"
      data-prisma-runtime-selector="data-pcinv-product-ficha"
      data-prisma-source-owner="inventory-workspace.tsx"
      data-prisma-css-owner="pc-inventory-master-detail.module.css"
      data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1"
    >
      <div className={styles.fichaHeader}>
        <div>
          <span className={styles.kicker}>acción rápida</span>
          <h2>{snapshot.productName}</h2>
        </div>
        <StatusBadge value={snapshot.stateLabel} />
      </div>
      <div className={styles.fichaStack}>
        <div className={styles.fichaRow}><span>SKU</span><strong>{snapshot.sku}</strong></div>
        <div className={styles.fichaRow}><span>Ubicación</span><strong>{snapshot.location}</strong></div>
        <div className={styles.fichaRow}><span>Existencia</span><strong>{qty(snapshot.onHand)}</strong></div>
        <div className={styles.fichaRow}><span>Reservado</span><strong>{qty(snapshot.reserved)}</strong></div>
        <div className={styles.fichaRow}><span>Disponible</span><strong>{qty(snapshot.available)}</strong></div>
        <div className={styles.fichaRow}><span>Cobertura</span><strong>{snapshot.daysCoverLabel}</strong></div>
      </div>
      <div className={styles.actionRail} data-pcinv-action-rail="stock">
        <a href={queryHref("/counts", { q: snapshot.sku })}>Crear conteo</a>
        <a href={queryHref("/stock", { q: snapshot.sku, state: "critical" })}>Revisar reabasto</a>
        <a href={queryHref("/auditoria-inventario", { q: snapshot.sku })}>Auditoría</a>
        <span aria-disabled="true" title="El ajuste directo todavía no está disponible desde esta pantalla.">Ajuste directo no disponible</span>
      </div>
    </section>
  );
}

function InventoryIntentBar({ view, workspace, path }: { view: InventoryWorkspaceViewName; workspace: InventoryWorkspace; path: string }) {
  const locations = uniqueLocations(workspace);
  if (view === "audit") {
    return (
      <section className={styles.intentBar} data-pcinv-search-first="audit">
        <form className={styles.searchBox} action={path}>
          <label htmlFor="audit-q">Buscar SKU, usuario o acción</label>
          <input id="audit-q" name="q" defaultValue={workspace.filters.q === "all" ? "" : workspace.filters.q} placeholder="Ej. COCA600, Juan, ajuste..." />
          <button type="submit">Buscar</button>
        </form>
        <div className={styles.chipStack} data-pcinv-chip-controls="audit-severity">
          <a href={queryHref(path, { ...workspace.filters, auditSeverity: "all" })}>Todos</a>
          <a href={queryHref(path, { ...workspace.filters, auditSeverity: "critical" })}>Críticos</a>
          <a href={queryHref(path, { ...workspace.filters, auditSeverity: "warn" })}>Revisar</a>
          <a href={queryHref(path, { ...workspace.filters, auditSeverity: "info" })}>Informativos</a>
        </div>
      </section>
    );
  }

  if (view === "counts") {
    return (
      <section className={styles.intentBar} data-pcinv-search-first="counts">
        <form className={styles.searchBox} action={path}>
          <label htmlFor="counts-q">Buscar SKU o ubicación</label>
          <input id="counts-q" name="q" defaultValue={workspace.filters.q === "all" ? "" : workspace.filters.q} placeholder="Producto, SKU o almacén..." />
          <button type="submit">Buscar</button>
        </form>
        <div className={styles.chipStack} data-pcinv-chip-controls="count-status">
          <a href={queryHref(path, { ...workspace.filters, countStatus: "all" })}>Todos</a>
          <a href={queryHref(path, { ...workspace.filters, countStatus: "open" })}>Abiertos</a>
          <a href={queryHref(path, { ...workspace.filters, countStatus: "variance" })}>Con diferencia</a>
          <a href={queryHref(path, { ...workspace.filters, countStatus: "closed" })}>Cerrados</a>
        </div>
      </section>
    );
  }

  return (
    <section className={styles.intentBar} data-pcinv-search-first="stock">
      <form className={styles.searchBox} action={path}>
        <label htmlFor="stock-q">Buscar SKU, producto o código</label>
        <input id="stock-q" name="q" defaultValue={workspace.filters.q === "all" ? "" : workspace.filters.q} placeholder="Ej. SKU, nombre o código..." />
        <button type="submit">Buscar</button>
      </form>
      <div className={styles.chipStack} data-pcinv-chip-controls="stock-state">
        <a href={queryHref(path, { ...workspace.filters, state: "all" })}>Todos</a>
        <a href={queryHref(path, { ...workspace.filters, state: "critical" })}>Cero/crítico</a>
        <a href={queryHref(path, { ...workspace.filters, state: "low" })}>Bajo mínimo</a>
        <a href={queryHref(path, { ...workspace.filters, state: "over" })}>Sobrante</a>
      </div>
      {locations.length ? (
        <div className={styles.chipStack} data-pcinv-chip-controls="stock-location">
          <a href={queryHref(path, { ...workspace.filters, location: "all" })}>Todas las ubicaciones</a>
          {locations.map((location) => <a key={location} href={queryHref(path, { ...workspace.filters, location })}>{location}</a>)}
        </div>
      ) : null}
    </section>
  );
}

export function InventoryWorkspaceView({
  view,
  workspace,
  currentPath: currentPathOverride
}: {
  view: InventoryWorkspaceViewName;
  workspace: InventoryWorkspace;
  currentPath?: string;
}) {
  const path = currentPath(view, currentPathOverride);
  const selectedSnapshot = firstSnapshot(workspace);

  return (
    <AppShell currentPath={path}>
      <main className={styles.inventoryShell} data-pcinv-ux-minimal-controls="inventory" data-pcinv-master-detail="inventory" data-pcinv-view={view}>
        <section className={styles.slimHeader}>
          <div>
            <span className={styles.kicker}>inventario operativo</span>
            <h1>{titleFor(view)}</h1>
            <p>{copyFor(view)}</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{workspace.summary.stockedSkuCount}</strong> SKUs</span>
            <span><strong>{workspace.summary.criticalStockCount}</strong> críticos</span>
            <span><strong>{pct(workspace.summary.inventoryAccuracy)}</strong> exactitud</span>
          </div>
        </section>

        <InventoryIntentBar view={view} workspace={workspace} path={path} />

        {workspace.meta.warnings.length ? (
          <div className={styles.honestBlock} role="status">
            <strong>Información temporalmente no disponible</strong>
            <p>{workspace.meta.warnings.join(" · ")}</p>
          </div>
        ) : null}

        {view === "stock" ? <StockPanel workspace={workspace} selectedSnapshot={selectedSnapshot} /> : null}
        {view === "counts" ? <CountsPanel workspace={workspace} /> : null}
        {view === "audit" ? <AuditPanel workspace={workspace} /> : null}
      </main>
    </AppShell>
  );
}

function StockPanel({ workspace, selectedSnapshot }: { workspace: InventoryWorkspace; selectedSnapshot: StockSnapshotView | null }) {
  return (
    <section className={styles.masterDetailTight} data-pcinv-dense-product-list="stock">
      <section className={styles.productLedger}>
        <div className={styles.ledgerHeader}>
          <div>
            <span className={styles.kicker}>existencias</span>
            <h2>Existencias por SKU y ubicación</h2>
            <p>Disponible, reservado, cobertura y estado por ubicación.</p>
          </div>
          <StatusBadge value={workspace.summary.criticalStockCount ? "crítico" : "ok"} />
        </div>
        <div className={styles.tableFrame}>
          <DataTable
            columns={["SKU", "Producto", "Ubicación", "Disponible", "Reservado", "Cobertura", "Estado"]}
            rows={workspace.snapshots.map((row) => ({
              SKU: row.sku,
              Producto: row.productName,
              Ubicación: row.location,
              Disponible: qty(row.available),
              Reservado: qty(row.reserved),
              Cobertura: row.daysCoverLabel,
              Estado: row.stateLabel,
              __rowDetailTitle: row.productName,
              __rowDetailTone: snapshotTone(row),
              __rowDetailItems: [
                `Existencia ${qty(row.onHand)} y reservado ${qty(row.reserved)}`,
                `Corte ${row.snapshotAtLabel}`,
                row.state === "critical" ? "Siguiente acción: revisar conteo o reabasto" : "Siguiente acción: mantener seguimiento"
              ],
              __rowActionHref: queryHref("/stock", { q: row.sku, location: row.location }),
              __rowActionLabel: "Abrir acción"
            }))}
            emptyMessage="No hay cortes de inventario para los criterios actuales."
          />
        </div>
      </section>

      <StockFicha snapshot={selectedSnapshot} />

      <section className={styles.workflowPanel} data-pcinv-movement-ledger="stock">
        <div className={styles.panelHeader}>
          <div>
            <span className={styles.kicker}>movimientos</span>
            <h2>Últimos movimientos</h2>
          </div>
        </div>
        <div className={styles.tableFrame}>
          <DataTable
            columns={["Fecha", "SKU", "Movimiento", "Cantidad", "Antes", "Después", "Motivo"]}
            rows={workspace.ledger.slice(0, 18).map((row) => ({
              Fecha: row.createdAtLabel,
              SKU: row.sku,
              Movimiento: row.movement,
              Cantidad: qty(row.quantityDelta),
              Antes: row.beforeQty === null ? "calculado" : qty(row.beforeQty),
              Después: row.afterQty === null ? "calculado" : qty(row.afterQty),
              Motivo: row.reason
            }))}
            emptyMessage="No hay movimientos para los criterios actuales."
          />
        </div>
      </section>
    </section>
  );
}

function CountsPanel({ workspace }: { workspace: InventoryWorkspace }) {
  return (
    <section className={styles.countConsole} data-pcinv-count-console="counts">
      <section className={styles.workflowPanel}>
        <div className={styles.panelHeader}>
          <div><span className={styles.kicker}>flujo</span><h2>Conteo físico guiado</h2></div>
        </div>
        <div className={styles.workflowStack}>
          {["Elegir ubicación", "Capturar conteo", "Comparar diferencia", "Asignar motivo", "Cerrar con evidencia"].map((label, index) => (
            <div className={styles.workflowStep} key={label}>
              <span className={styles.stepIndex}>{index + 1}</span>
              <div><strong>{label}</strong><span>{index < 3 ? "Disponible para consulta" : "Esta acción todavía no está disponible desde esta pantalla"}</span></div>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.productLedger}>
        <div className={styles.ledgerHeader}>
          <div><span className={styles.kicker}>conteos</span><h2>Diferencias por ubicación</h2></div>
          <StatusBadge value={workspace.summary.openCountCount ? "pendiente" : "ok"} />
        </div>
        <div className={styles.tableFrame}>
          <DataTable
            columns={["Fecha", "Ubicación", "Contó", "Variación", "Exactitud", "Estado"]}
            rows={workspace.counts.map((row) => ({
              Fecha: row.countedAtLabel,
              Ubicación: row.location,
              Contó: row.countedBy,
              Variación: qty(row.variance),
              Exactitud: row.accuracyLabel,
              Estado: row.status,
              __rowDetailTitle: `Conteo en ${row.location}`,
              __rowDetailTone: Math.abs(row.variance) > 0 ? "warn" : "ok",
              __rowDetailItems: [`Variación ${qty(row.variance)}`, `Responsable ${row.countedBy}`, "Si existe diferencia, el cierre debe incluir un motivo."],
              __rowActionHref: queryHref("/counts", { location: row.location, status: row.status }),
              __rowActionLabel: "Abrir conteo"
            }))}
            emptyMessage="No hay conteos para los criterios actuales."
          />
        </div>
      </section>

      <section className={styles.priorityPanel}>
        <div className={styles.panelHeader}>
          <div><span className={styles.kicker}>diferencias</span><h2>Riesgos por conteo</h2></div>
        </div>
        {workspace.countFindings.length ? (
          <div className={styles.queueStack}>
            {workspace.countFindings.map((finding) => (
              <div className={styles.queueRow} key={finding.id}>
                <StatusBadge value={finding.severity} />
                <div><strong>{finding.title}</strong><span>{finding.detail}</span></div>
                <a className="footer-chip" href={queryHref("/auditoria-inventario", { q: finding.entityLabel })}>Auditar</a>
              </div>
            ))}
          </div>
        ) : <EmptyState title="Sin diferencias críticas." description="Los conteos cargados no tienen hallazgos graves para los criterios actuales." />}
      </section>
    </section>
  );
}

function AuditPanel({ workspace }: { workspace: InventoryWorkspace }) {
  return (
    <section className={styles.auditTimeline} data-pcinv-audit-workbench="inventory">
      <section className={styles.auditPanel}>
        <div className={styles.panelHeader}>
          <div><span className={styles.kicker}>hallazgos</span><h2>Cola por severidad</h2></div>
          <StatusBadge value={workspace.auditFindings.length ? "revisar" : "ok"} />
        </div>
        <div className={styles.queueStack}>
          {workspace.auditFindings.length ? workspace.auditFindings.map((finding) => (
            <div className={styles.timelineEvent} key={finding.id}>
              <StatusBadge value={finding.severity} />
              <div>
                <strong>{finding.title}</strong>
                <span>{finding.entityLabel}</span>
                <p>{finding.detail}</p>
                <a className="footer-chip" href={queryHref("/auditoria-inventario", { q: finding.entityLabel, severity: finding.severity })}>Filtrar hallazgo</a>
              </div>
            </div>
          )) : <EmptyState title="Sin hallazgos." description="No hay eventos sensibles para los criterios actuales." />}
        </div>
      </section>

      <section className={styles.workflowPanel}>
        <div className={styles.panelHeader}>
          <div><span className={styles.kicker}>historial</span><h2>Movimientos sensibles</h2></div>
        </div>
        <div className={styles.timelineStack} data-pcinv-timeline="audit">
          {workspace.ledger.slice(0, 20).map((row) => (
            <article className={styles.timelineEvent} key={`${row.createdAtLabel}-${row.sku}-${row.movement}`}>
              <span className={styles.timelineDot} />
              <div>
                <strong>{row.movement} · {row.sku}</strong>
                <span>{row.createdAtLabel} · {row.actor}</span>
                <p>Antes: {row.beforeQty === null ? "calculado" : qty(row.beforeQty)} · Después: {row.afterQty === null ? "calculado" : qty(row.afterQty)} · Motivo: {row.reason}</p>
              </div>
            </article>
          ))}
        </div>
        <div className={styles.honestBlock} style={{ marginTop: 14 }}>
          <strong>Corrección no disponible desde esta vista</strong>
          <p>La auditoría permite revisar el historial. Los cambios de inventario deben realizarse desde una acción autorizada que registre responsable, motivo y valores antes y después.</p>
        </div>
      </section>
    </section>
  );
}
