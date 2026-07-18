import { AppShell } from "@components/layout/app-shell";
import { StatusBadge } from "@components/backoffice/status-badge";
import { pcI07ValidationData } from "@/lib/i07/validation-data";
import { badgeTone } from "@/lib/i07/validation-helpers";
import styles from "@components/inventory/pc-inventory-master-detail.module.css";

export default function ValidacionCatalogoPage() {
  const totals = pcI07ValidationData.totals;
  const queue = [
    { label: "Códigos duplicados", value: totals.duplicate_codes, area: "barcode", action: "Bloquear sync si afecta venta" },
    { label: "SKUs sin código", value: totals.active_without_barcode, area: "barcode", action: "Abrir salud de barcodes" },
    { label: "Precio menor a costo", value: totals.negative_margin, area: "precio", action: "Revisar política de precios" },
    { label: "Precio cero o negativo", value: totals.zero_or_negative_price, area: "precio", action: "Bloquear venta hasta corrección" },
    { label: "Quiebres visibles", value: totals.stockout_slots, area: "stock", action: "Mandar a reabasto" }
  ];

  return (
    <AppShell currentPath="/validacion-catalogo">
      <main className={styles.inventoryShell} data-pcinv-ux-minimal-controls="validation" data-pcinv-quality-workbench="validation">
        <section className={styles.slimHeader}>
          <div>
            <span className={styles.kicker}>semáforo de datos</span>
            <h1>Validación de catálogo</h1>
            <p>Cola de calidad por severidad y área. Chips para orientar, no dropdowns para disfrazar.</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{pcI07ValidationData.headline.criticalIncidents}</strong> críticos</span>
            <span><strong>{pcI07ValidationData.headline.reviewQueue}</strong> en cola</span>
            <span><strong>{totals.active_products}</strong> SKUs</span>
          </div>
        </section>

        <section className={styles.intentBar} data-pcinv-chip-controls="validation-severity">
          <div className={styles.chipStack}>
            <a href="/validacion-catalogo">Todos</a>
            <a href="/validacion-catalogo?severity=critical">Crítico</a>
            <a href="/validacion-catalogo?severity=review">Revisar</a>
            <a href="/validacion-catalogo?severity=info">Informativo</a>
          </div>
          <div className={styles.chipStack} data-pcinv-chip-controls="validation-area">
            <a href="/validacion-catalogo?area=precio">Precio</a>
            <a href="/validacion-catalogo?area=barcode">Barcode</a>
            <a href="/validacion-catalogo?area=stock">Stock</a>
            <a href="/validacion-catalogo?area=proveedor">Proveedor</a>
          </div>
        </section>

        <section className={styles.validationConsole}>
          <section className={styles.qualityPanelCompact}>
            <div className={styles.panelHeader}><div><span className={styles.kicker}>cola</span><h2>Incidentes accionables</h2></div><StatusBadge value={pcI07ValidationData.headline.criticalIncidents ? "crítico" : "ok"} /></div>
            <div className={styles.queueStack}>{queue.map((item) => <div className={styles.queueRow} key={item.label}><strong>{item.value}</strong><div><strong>{item.label}</strong><span>{item.action}</span></div><a className="footer-chip" href={item.area === "barcode" ? "/salud-barcodes" : item.area === "stock" ? "/stock?state=critical" : "/catalog"}>Abrir</a></div>)}</div>
          </section>
          <section className={styles.workflowPanel}><div className={styles.panelHeader}><div><span className={styles.kicker}>corrección segura</span><h2>Regla de operación</h2></div><StatusBadge value={badgeTone(pcI07ValidationData.headline.criticalIncidents)} /></div><div className={styles.workflowStack}>{["Detectar", "Abrir entidad", "Validar impacto", "Corregir con motivo", "Auditar y sincronizar"].map((step, index) => <div className={styles.workflowStep} key={step}><span className={styles.stepIndex}>{index + 1}</span><div><strong>{step}</strong><span>{index < 3 ? "Lectura disponible" : "Requiere endpoint auditable"}</span></div></div>)}</div></section>
        </section>
      </main>
    </AppShell>
  );
}
