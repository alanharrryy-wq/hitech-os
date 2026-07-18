import { DataTable } from "@components/backoffice/data-table";
import { StatusBadge } from "@components/backoffice/status-badge";
import { AppShell } from "@components/layout/app-shell";
import { getBarcodeHealthRows } from "@/lib/services/catalog";
import styles from "@components/inventory/pc-inventory-master-detail.module.css";

export const dynamic = "force-dynamic";

export default async function SaludBarcodesPage() {
  const { rows: barcodeHealthRows, notice } = await getBarcodeHealthRows();
  const totalProducts = barcodeHealthRows.reduce((acc, row) => acc + Number(row.productos ?? 0), 0);
  const totalCodes = barcodeHealthRows.reduce((acc, row) => acc + Number(row.barcodes ?? 0), 0);

  return (
    <AppShell currentPath="/salud-barcodes">
      <main className={styles.inventoryShell} data-pcinv-ux-minimal-controls="barcodes" data-pcinv-barcode-workbench="health">
        <section className={styles.slimHeader}>
          <div>
            <span className={styles.kicker}>mesa de corrección</span>
            <h1>Salud de barcodes</h1>
            <p>Cobertura real de códigos por categoría. La corrección se mantiene bloqueada hasta que exista un comando auditable.</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{totalProducts}</strong> productos</span>
            <span><strong>{totalCodes}</strong> códigos</span>
          </div>
        </section>

        <section className={styles.intentBar} data-pcinv-barcode-health="aggregate">
          <span className={styles.subtle}>Esta vista es una agregación de lecturas canónicas; no simula búsquedas, filtros ni guardados sin un owner durable.</span>
        </section>

        {notice ? <div className={styles.honestBlock}><strong>{notice.title}</strong><p>{notice.detail}</p></div> : null}

        <section className={styles.barcodeWorkbench}>
          <section className={styles.productLedger}>
            <div className={styles.ledgerHeader}><div><span className={styles.kicker}>problemas</span><h2>Cobertura por categoría</h2></div><StatusBadge value={totalCodes ? "ok" : "revisar"} /></div>
            <div className={styles.tableFrame}>
              <DataTable columns={["Categoría", "Productos", "Códigos", "Promedio", "Activos"]} rows={barcodeHealthRows.map((row) => ({ Categoría: row.categoria, Productos: row.productos, Códigos: row.barcodes, Promedio: row.promedio, Activos: row.activos, __rowDetailTitle: row.categoria, __rowDetailTone: Number(row.promedio) < 1 ? "warn" : "ok", __rowDetailItems: [`${row.productos} productos`, `${row.barcodes} códigos`, "Siguiente acción: revisar SKUs sin código."], __rowActionHref: `/catalog?category=${encodeURIComponent(row.categoria)}`, __rowActionLabel: "Abrir categoría" }))} emptyMessage="No hay códigos de barras consolidados disponibles en esta lectura." />
            </div>
          </section>
          <section className={styles.productFicha} data-pcinv-correction-panel="barcode">
            <div className={styles.fichaHeader}><div><span className={styles.kicker}>siguiente paso</span><h2>Corrección gobernada pendiente</h2></div></div>
            <div className={styles.fichaStack}>
              <div className={styles.fichaRow}><span>Validación</span><strong>duplicados</strong></div>
              <div className={styles.fichaRow}><span>Motivo</span><strong>obligatorio</strong></div>
              <div className={styles.fichaRow}><span>Sync</span><strong>delta a Tablet</strong></div>
            </div>
            <div className={styles.actionRail}><a href="/validacion-catalogo">Ver validación</a><span aria-disabled="true">Guardar bloqueado hasta endpoint auditable</span></div>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
