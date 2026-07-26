/* PRISMA_DARK_PACKSHOTS_197 */
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { StatusBadge } from "@components/backoffice/status-badge";
import { AppShell } from "@components/layout/app-shell";
import { ProductVariantWorkspace } from "@components/catalog/product-variant-workspace";
import { ProductMediaWorkspace } from "@components/catalog/product-media-workspace";
import type { CatalogProductRecord, CatalogWorkspace } from "@/modules/catalog/types";
import type { getProductVariantWorkspace } from "@/server/services/product-variant.service";
import type { getProductMediaWorkspace } from "@/server/services/product-media.service";
import styles from "../inventory/pc-inventory-master-detail.module.css";
import mediaStyles from "./product-media-workspace.module.css";
import mediaStyles from "./product-media-workspace.module.css";

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function margin(product: CatalogProductRecord) {
  if (!product.priceCents) return "sin precio";
  const value = ((product.priceCents - product.costCents) / product.priceCents) * 100;
  return `${new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 }).format(value)}%`;
}

function coverageLabel(daysCover: number | null) {
  if (daysCover === null) return "sin corte";
  if (daysCover < 1) return "crítico";
  if (daysCover < 3) return "riesgo";
  return "estable";
}

function queryHref(path: string, params: Record<string, string>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value !== "all") query.set(key, value);
  });
  const text = query.toString();
  return text ? `${path}?${text}` : path;
}

function productTone(product: CatalogProductRecord) {
  if (product.issues.some((issue) => issue.severity === "ALTO")) return "danger" as const;
  if (product.issues.length || !product.isActive) return "warn" as const;
  return "ok" as const;
}

function CatalogProductFicha({ product }: { product: CatalogProductRecord | null }) {
  if (!product) {
    return (
      <section className={styles.productFicha} data-pcinv-product-ficha="empty">
        <div className={styles.fichaHeader}>
          <div>
            <span className={styles.kicker}>ficha de producto</span>
            <h2>Sin SKU seleccionado</h2>
          </div>
        </div>
        <EmptyState title="Selecciona un producto." description="Usa la búsqueda o la lista densa de SKUs para abrir una ficha lateral con precio, stock, códigos, margen y acciones honestas." />
      </section>
    );
  }

  return (
    <section className={styles.productFicha} data-pcinv-product-ficha="catalog">
      <div className={styles.fichaHeader}>
        <div>
          <span className={styles.kicker}>ficha del SKU</span>
          <h2>{product.name}</h2>
        </div>
        <StatusBadge value={product.isActive ? "activo" : "inactivo"} />
      </div>

      <div className={mediaStyles.preview}>
        {product.mediaRef ? <img src={product.mediaRef} alt={`Imagen de ${product.name}`} /> : <span>Sin imagen asignada</span>}
        <div><strong>Imagen del catálogo</strong><small>{product.mediaRef ?? "Elige una imagen en la biblioteca inferior."}</small></div>
      </div>

      <div className={mediaStyles.preview}>
        {product.mediaRef ? <img src={product.mediaRef} alt={`Imagen de ${product.name}`} /> : <span>Sin imagen asignada</span>}
        <div><strong>Imagen del catálogo</strong><small>{product.mediaRef ?? "Elige una imagen en la biblioteca inferior."}</small></div>
      </div>

      <div className={styles.fichaStack}>
        <div className={styles.fichaRow}><span>SKU</span><strong>{product.sku}</strong></div>
        <div className={styles.fichaRow}><span>Categoría</span><strong>{product.category}</strong></div>
        <div className={styles.fichaRow}><span>Precio</span><strong>{money(product.priceCents)}</strong></div>
        <div className={styles.fichaRow}><span>Costo</span><strong>{money(product.costCents)}</strong></div>
        <div className={styles.fichaRow}><span>Margen</span><strong>{margin(product)}</strong></div>
        <div className={styles.fichaRow}><span>Existencia</span><strong>{product.stockOnHand}</strong></div>
        <div className={styles.fichaRow}><span>Cobertura</span><strong>{coverageLabel(product.daysCover)}</strong></div>
        <div className={styles.fichaRow}><span>Códigos</span><strong>{product.barcodes.length ? product.barcodes.join(", ") : "sin código"}</strong></div>
      </div>

      <div className={styles.internalTabs} data-pcinv-internal-tabs="catalog">
        <span>Resumen</span>
        <a href={queryHref("/stock", { q: product.sku })}>Stock</a>
        <a href={queryHref("/movements", { q: product.sku })}>Movimientos</a>
        <a href={queryHref("/salud-barcodes", { q: product.sku })}>Barcodes</a>
        <a href={queryHref("/auditoria-inventario", { q: product.sku })}>Auditoría</a>
      </div>

      <div className={styles.actionRail} data-pcinv-action-rail="catalog">
        <a href={queryHref("/stock", { q: product.sku, state: "all" })}>Ajustar stock</a>
        <a href={queryHref("/salud-barcodes", { q: product.sku })}>Agregar barcode</a>
        <a href={queryHref("/counts", { q: product.sku })}>Crear conteo</a>
        <a href={queryHref("/stock", { q: product.sku, state: "critical" })}>Mandar a reabasto</a>
        <span aria-disabled="true" title="Editar producto requiere endpoint auditable con rol, motivo y before/after.">Editar bloqueado hasta auditoría</span>
      </div>

      {product.issues.length ? (
        <div className={styles.qualityStack} style={{ marginTop: 14 }}>
          {product.issues.map((issue) => (
            <div className={styles.honestBlock} key={`${product.sku}-${issue.type}`}>
              <strong>{issue.label}</strong>
              <p>{issue.detail}</p>
              <small>{issue.recommendedAction}</small>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}

export function CatalogDashboard({ workspace, productVariantWorkspace, productMediaWorkspace }: { workspace: CatalogWorkspace; productVariantWorkspace: Awaited<ReturnType<typeof getProductVariantWorkspace>>; productMediaWorkspace: Awaited<ReturnType<typeof getProductMediaWorkspace>> }) {
  const selected = workspace.selectedProduct ?? workspace.products[0] ?? null;
  const issueChips = [
    { label: "Todos", href: queryHref("/catalog", { ...workspace.filters, issue: "all" }) },
    { label: "Con problema", href: queryHref("/catalog", { ...workspace.filters, issue: "problem" }) },
    { label: "Sin código", href: queryHref("/catalog", { ...workspace.filters, issue: "missing_barcode" }) },
    { label: "Precio raro", href: queryHref("/catalog", { ...workspace.filters, issue: "price" }) },
    { label: "Sin stock", href: queryHref("/catalog", { ...workspace.filters, issue: "stock" }) }
  ];
  const stateChips = [
    { label: "Activos", href: queryHref("/catalog", { ...workspace.filters, status: "active" }) },
    { label: "Inactivos", href: queryHref("/catalog", { ...workspace.filters, status: "inactive" }) },
    { label: "Todos", href: queryHref("/catalog", { ...workspace.filters, status: "all" }) }
  ];
  const rows = workspace.products.map((product) => ({
    SKU: product.sku,
    Producto: product.name,
    Categoría: product.category,
    Imagen: product.mediaRef ? "asignada" : "sin imagen",
    Precio: money(product.priceCents),
    Margen: margin(product),
    Códigos: product.barcodes.length,
    Stock: product.stockOnHand,
    Cobertura: coverageLabel(product.daysCover),
    Estado: product.isActive ? "activo" : "inactivo",
    __rowDetailTitle: product.name,
    __rowDetailTone: productTone(product),
    __rowDetailItems: [
      `Precio ${money(product.priceCents)} contra costo ${money(product.costCents)}`,
      `Códigos: ${product.barcodes.length ? product.barcodes.join(", ") : "sin código"}`,
      `Acción sugerida: ${product.issues[0]?.recommendedAction ?? "Mantener en catálogo activo"}`
    ],
    __rowActionHref: queryHref("/catalog", { ...workspace.filters, selectedSku: product.sku }),
    __rowActionLabel: "Abrir ficha"
  }));

  return (
    <AppShell currentPath="/catalog">
      <main className={styles.inventoryShell} data-pcinv-ux-minimal-controls="catalog" data-pcinv-master-detail="catalog" data-pcinv-dense-product-list="catalog">
        <section className={styles.slimHeader}>
          <div>
            <span className={styles.kicker}>inventario maestro</span>
            <h1>Catálogo operativo</h1>
            <p>Buscar, detectar problema, abrir ficha y actuar. Sin dock de selectores como aduana.</p>
          </div>
          <div className={styles.miniStats}>
            <span><strong>{workspace.summary.totalProducts}</strong> SKUs</span>
            <span><strong>{workspace.summary.missingBarcodeCount}</strong> sin código</span>
            <span><strong>{workspace.summary.duplicateBarcodeCount}</strong> duplicados</span>
          </div>
        </section>

        <section className={styles.intentBar} data-pcinv-search-first="catalog">
          <form className={styles.searchBox} action="/catalog">
            <label htmlFor="catalog-q">Buscar SKU, producto o barcode</label>
            <input id="catalog-q" name="q" defaultValue={workspace.filters.q === "all" ? "" : workspace.filters.q} placeholder="Ej. COCA600, Coca-Cola, 750105..." />
            <button type="submit">Buscar</button>
          </form>
          <div className={styles.chipStack} data-pcinv-chip-controls="catalog-status">
            {stateChips.map((chip) => <a key={chip.label} href={chip.href}>{chip.label}</a>)}
          </div>
          <div className={styles.chipStack} data-pcinv-chip-controls="catalog-issues">
            {issueChips.map((chip) => <a key={chip.label} href={chip.href}>{chip.label}</a>)}
          </div>
        </section>

        {workspace.meta.warnings.length ? (
          <div className={styles.honestBlock} role="status">
            <strong>Estado honesto</strong>
            <p>{workspace.meta.warnings.join(" · ")}</p>
          </div>
        ) : null}

        <section className={styles.masterDetailTight}>
          <section className={styles.productLedger}>
            <div className={styles.ledgerHeader}>
              <div>
                <span className={styles.kicker}>lista densa</span>
                <h2>Productos operables</h2>
                <p>La tabla manda. Los filtros finos viven dentro de búsqueda, chips o ficha.</p>
              </div>
              <StatusBadge value={workspace.exceptions.length ? "riesgo" : "ok"} />
            </div>
            <div className={styles.tableFrame}>
              <DataTable
                columns={["SKU", "Producto", "Categoría", "Imagen", "Precio", "Margen", "Códigos", "Stock", "Cobertura", "Estado"]}
                rows={rows}
                emptyMessage="No hay productos para los criterios actuales."
              />
            </div>
            <div className={styles.skuRail}>
              {workspace.products.slice(0, 10).map((product) => (
                <a key={product.sku} href={queryHref("/catalog", { ...workspace.filters, selectedSku: product.sku })}>{product.sku}</a>
              ))}
            </div>
          </section>

          <CatalogProductFicha product={selected} />
        </section>

        <section className={styles.qualityPanelCompact} data-pcinv-quality-workbench="catalog">
          <div className={styles.panelHeader}>
            <div>
              <span className={styles.kicker}>calidad de datos</span>
              <h2>Incidencias accionables</h2>
              <p>Se revisa como cola de trabajo, no como otro tablero lleno de filtros.</p>
            </div>
            <a className="footer-chip" href="/validacion-catalogo">Abrir validación</a>
          </div>
          <div className={styles.tableFrame}>
            <DataTable
              columns={["Severidad", "SKU", "Producto", "Tipo", "Detalle", "Acción"]}
              rows={workspace.exceptions.map((issue) => ({
                Severidad: issue.severity,
                SKU: issue.sku,
                Producto: issue.productName,
                Tipo: issue.label,
                Detalle: issue.detail,
                Acción: issue.recommendedAction,
                __rowDetailTitle: issue.label,
                __rowDetailTone: issue.severity === "ALTO" ? "danger" : "warn",
                __rowDetailItems: [issue.detail, issue.recommendedAction],
                __rowActionHref: queryHref("/catalog", { selectedSku: issue.sku, issue: issue.type }),
                __rowActionLabel: "Abrir SKU"
              }))}
              emptyMessage="No hay incidencias con los criterios actuales."
            />
          </div>
        </section>

        <ProductVariantWorkspace initialWorkspace={productVariantWorkspace} />
        <ProductMediaWorkspace initialWorkspace={productMediaWorkspace} />
      </main>
    </AppShell>
  );
}
