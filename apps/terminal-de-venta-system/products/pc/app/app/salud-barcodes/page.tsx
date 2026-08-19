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
            <span className={styles.kicker}>calidad del catálogo</span>
            <h1>Salud de códigos</h1>
            <p>Revisa la cobertura de códigos por categoría y encuentra productos que requieren atención.</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{totalProducts}</strong> productos</span>
            <span><strong>{totalCodes}</strong> códigos</span>
          </div>
        </section>

        <section className={styles.intentBar} data-pcinv-barcode-health="aggregate">
          <span className={styles.subtle}>La información se presenta por categoría para facilitar la revisión y priorización.</span>
        </section>

        {notice ? <div className={styles.honestBlock} role="status"><strong>Información temporalmente no disponible</strong><p>{notice.detail}</p></div> : null}

        <section className={styles.barcodeWorkbench}>
          <section className={styles.productLedger}>
            <div className={styles.ledgerHeader}><div><span className={styles.kicker}>cobertura</span><h2>Códigos por categoría</h2></div><StatusBadge value={totalCodes ? "ok" : "revisar"} /></div>
            <div className={styles.tableFrame}>
              <DataTable columns={["Categoría", "Productos", "Códigos", "Promedio", "Activos"]} rows={barcodeHealthRows.map((row) => ({ Categoría: row.categoria, Productos: row.productos, Códigos: row.barcodes, Promedio: row.promedio, Activos: row.activos, __rowDetailTitle: row.categoria, __rowDetailTone: Number(row.promedio) < 1 ? "warn" : "ok", __rowDetailItems: [`${row.productos} productos`, `${row.barcodes} códigos`, "Siguiente acción: revisar productos sin código."], __rowActionHref: `/catalog?category=${encodeURIComponent(row.categoria)}`, __rowActionLabel: "Abrir categoría" }))} emptyMessage="No hay códigos disponibles para mostrar en esta lectura." />
            </div>
          </section>
          <section className={styles.productFicha} data-pcinv-correction-panel="barcode">
            <div className={styles.fichaHeader}><div><span className={styles.kicker}>siguiente paso</span><h2>Revisión de productos</h2></div></div>
            <div className={styles.fichaStack}>
              <div className={styles.fichaRow}><span>Duplicados</span><strong>revisar</strong></div>
              <div className={styles.fichaRow}><span>Productos sin código</span><strong>revisar</strong></div>
              <div className={styles.fichaRow}><span>Actualización</span><strong>desde catálogo</strong></div>
            </div>
            <div className={styles.actionRail}><a href="/catalog?issue=problem">Abrir catálogo con incidencias</a><span aria-disabled="true">Edición directa no disponible aquí</span></div>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
