import { DataTable } from "@components/backoffice/data-table";
import { StatusBadge } from "@components/backoffice/status-badge";
import { AppShell } from "@components/layout/app-shell";
import { getCriticalStockRows } from "@/lib/services/catalog";
import styles from "@components/inventory/pc-inventory-master-detail.module.css";

export const dynamic = "force-dynamic";

export default async function ExistenciasCriticasPage() {
  const { rows: criticalStockRows, notice } = await getCriticalStockRows();
  const first = criticalStockRows[0] ?? null;
  const zeroRows = criticalStockRows.filter((row) => Number(row.disponible ?? 0) <= 0).length;
  const urgentRows = criticalStockRows.filter((row) => Number(row.diasCobertura ?? 99) <= 3).length;

  return (
    <AppShell currentPath="/existencias-criticas">
      <main className={styles.inventoryShell} data-pcinv-ux-minimal-controls="critical-stock" data-pcinv-priority-queue="critical-stock">
        <section className={styles.slimHeader}>
          <div>
            <span className={styles.kicker}>cola de compra</span>
            <h1>Productos que pueden romper venta</h1>
            <p>Prioridad, cobertura y acción directa. Aquí no hacen falta cinco dropdowns: hace falta saber qué comprar primero.</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{criticalStockRows.length}</strong> críticos</span>
            <span><strong>{zeroRows}</strong> en cero</span>
            <span><strong>{urgentRows}</strong> ≤ 3 días</span>
          </div>
        </section>

        <section className={styles.intentBar} data-pcinv-chip-controls="critical-urgency">
          <div className={styles.chipStack}>
            <a href="/existencias-criticas">Todos</a>
            <a href="/existencias-criticas?urgency=today">Hoy</a>
            <a href="/existencias-criticas?urgency=3days">3 días</a>
            <a href="/existencias-criticas?urgency=week">Esta semana</a>
          </div>
          <form className={styles.inlineBudget} action="/existencias-criticas">
            <label htmlFor="critical-budget">Presupuesto opcional</label>
            <input id="critical-budget" name="budget" inputMode="numeric" placeholder="$ 5,000" />
            <button type="submit">Simular prioridad</button>
          </form>
        </section>

        {notice ? <div className={styles.honestBlock}><strong>{notice.title}</strong><p>{notice.detail}</p></div> : null}

        <section className={styles.priorityQueueLayout}>
          <section className={styles.priorityPanel}>
            <div className={styles.panelHeader}>
              <div><span className={styles.kicker}>prioridad</span><h2>Atender primero</h2></div>
              <StatusBadge value={criticalStockRows.length ? "crítico" : "ok"} />
            </div>
            <div className={styles.priorityHeroItem}>
              <strong>{first ? first.producto : "Sin quiebres visibles"}</strong>
              <span>{first ? `${first.sku} · disponible ${first.disponible} · cobertura ${first.diasCobertura}` : "La cola está limpia en esta lectura."}</span>
              {first ? <a className="footer-chip" href={`/catalog?selectedSku=${encodeURIComponent(first.sku)}`}>Abrir ficha</a> : null}
            </div>
            <div className={styles.tableFrame}>
              <DataTable
                columns={["SKU", "Producto", "Ubicación", "Disponible", "Días", "Estado"]}
                rows={criticalStockRows.map((row) => ({
                  SKU: row.sku,
                  Producto: row.producto,
                  Ubicación: row.ubicacion,
                  Disponible: row.disponible,
                  Días: row.diasCobertura,
                  Estado: row.estado,
                  __rowDetailTitle: row.producto,
                  __rowDetailTone: String(row.estado).toLowerCase().includes("cr") ? "danger" : "warn",
                  __rowDetailItems: [`Disponible ${row.disponible}`, `Cobertura ${row.diasCobertura}`, "Siguiente acción: agregar a reabasto o conteo físico."],
                  __rowActionHref: `/catalog?selectedSku=${encodeURIComponent(row.sku)}`,
                  __rowActionLabel: "Abrir ficha"
                }))}
                emptyMessage="No hay existencias críticas disponibles en esta lectura."
              />
            </div>
          </section>

          <section className={styles.workflowPanel}>
            <div className={styles.panelHeader}><div><span className={styles.kicker}>acción</span><h2>Ruta corta</h2></div></div>
            <div className={styles.workflowStack}>
              {[
                "Confirmar existencia física",
                "Agregar a borrador de compra",
                "Ajustar mínimo si la demanda cambió",
                "Ignorar sólo con motivo",
                "Auditar después de recibir"
              ].map((label, index) => <div className={styles.workflowStep} key={label}><span className={styles.stepIndex}>{index + 1}</span><div><strong>{label}</strong><span>{index < 2 ? "Acción directa" : "Con evidencia"}</span></div></div>)}
            </div>
            <div className={styles.actionRail}>
              <a href="/replenishment">Armar reabasto</a>
              <a href="/stock">Ver stock</a>
              <a href="/catalog">Abrir catálogo</a>
            </div>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
