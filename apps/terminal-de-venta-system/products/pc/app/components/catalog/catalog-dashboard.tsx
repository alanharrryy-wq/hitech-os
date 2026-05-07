import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";
import { EmptyState } from "@components/backoffice/empty-state";
import { StatusBadge } from "@components/backoffice/status-badge";
import type { CatalogWorkspace } from "@/modules/catalog/types";

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(cents / 100);
}

function coverageLabel(daysCover: number | null) {
  if (daysCover === null) return "sin corte";
  if (daysCover < 1) return "crítico";
  if (daysCover < 3) return "riesgo";
  return "estable";
}

function hrefWith(params: Record<string, string>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value && value !== "all") query.set(key, value);
  });
  const text = query.toString();
  return text ? `/catalog?${text}` : "/catalog";
}

export function CatalogDashboard({ workspace }: { workspace: CatalogWorkspace }) {
  const selected = workspace.selectedProduct ?? workspace.products[0] ?? null;

  return (
    <AppShell currentPath="/catalog">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">catálogo avanzado</div>
            <h1 className="hero-title">Catálogo, SKUs y códigos de barras</h1>
            <p>
              Panel PC para gobernar productos, códigos de barras, precios, estados y excepciones sin bloquear la venta local de Tablet.
            </p>
          </div>
          <div className="inline-list">
            <span className="chip">Estado: {workspace.meta.persistence === "available" ? "datos disponibles" : "sin datos disponibles"}</span>
            <span className="chip">Actualizado: {workspace.meta.generatedAt}</span>
          </div>
        </div>
        <div className="hero-badges">
          <span className="alert-chip">SKUs activos visibles</span>
          <span className="alert-chip">Códigos faltantes y duplicados</span>
          <span className="alert-chip">Detalle operativo por SKU</span>
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
          <div className="kicker">catálogo</div>
          <div className="card-title">SKUs totales</div>
          <div className="metric">{workspace.summary.totalProducts}</div>
          <div className="metric-note">Productos encontrados por repositorio/servicio.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">vigencia</div>
          <div className="card-title">Activos</div>
          <div className="metric">{workspace.summary.activeProducts}</div>
          <div className="metric-note">Productos habilitados para gobierno operativo.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">códigos</div>
          <div className="card-title">Sin código</div>
          <div className="metric">{workspace.summary.missingBarcodeCount}</div>
          <div className="metric-note">Activos que pueden reventar en caja o recepción.</div>
        </article>
        <article className="card metric-card">
          <div className="kicker">códigos</div>
          <div className="card-title">Duplicados</div>
          <div className="metric">{workspace.summary.duplicateBarcodeCount}</div>
          <div className="metric-note">Códigos repetidos detectados en muestra operativa.</div>
        </article>
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">filtros</div>
            <h2 className="section-title">Búsqueda operativa</h2>
            <div className="section-copy">Filtra por texto, estado, categoría e incidencia. La URL guarda el contexto para compartir revisión.</div>
          </div>
        </div>
        <form className="dashboard-actions" action="/catalog">
          <label className="action-card">
            <strong>Buscar</strong>
            <input name="q" defaultValue={workspace.filters.q} placeholder="SKU, producto o código" />
          </label>
          <label className="action-card">
            <strong>Estado</strong>
            <select name="status" defaultValue={workspace.filters.status}>
              <option value="all">Todos</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </label>
          <label className="action-card">
            <strong>Categoría</strong>
            <select name="category" defaultValue={workspace.filters.category}>
              <option value="all">Todas</option>
              {workspace.categories.map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </label>
          <label className="action-card">
            <strong>Incidencia</strong>
            <select name="issue" defaultValue={workspace.filters.issue}>
              <option value="all">Todas</option>
              <option value="missing_barcode">Sin código</option>
              <option value="duplicate_barcode">Código duplicado</option>
              <option value="inactive_product">Producto inactivo</option>
              <option value="stale_price">Precio viejo</option>
            </select>
          </label>
          <button type="submit">Aplicar filtros</button>
          <a className="footer-chip" href="/catalog">Limpiar</a>
        </form>
      </section>

      <section className="grid cols-2">
        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">productos</div>
              <h2 className="section-title">SKUs visibles</h2>
              <div className="section-copy">Lista conectada a servicio de catálogo; no es overview decorativo.</div>
            </div>
          </div>
          {workspace.products.length ? (
            <DataTable
              columns={["SKU", "Producto", "Categoría", "Precio", "Códigos", "Existencias", "Cobertura", "Estado"]}
              rows={workspace.products.map((product) => ({
                SKU: product.sku,
                Producto: product.name,
                Categoría: product.category,
                Precio: money(product.priceCents),
                Códigos: product.barcodes.length,
                Existencias: product.stockOnHand,
                Cobertura: coverageLabel(product.daysCover),
                Estado: product.isActive ? "activo" : "inactivo"
              }))}
              emptyMessage="No hay productos para los filtros seleccionados."
            />
          ) : (
            <EmptyState title="Sin SKUs para mostrar." description="Ajusta filtros o carga catálogo canónico antes de auditar excepciones." />
          )}
          <div className="inline-list" style={{ marginTop: 14 }}>
            {workspace.products.slice(0, 8).map((product) => (
              <a className="footer-chip" key={product.sku} href={hrefWith({ ...workspace.filters, sku: product.sku })}>{product.sku}</a>
            ))}
          </div>
        </article>

        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">detalle</div>
              <h2 className="section-title">Ficha del SKU</h2>
              <div className="section-copy">Muestra códigos, precio, estado, existencias y alertas accionables.</div>
            </div>
          </div>
          {selected ? (
            <div className="list">
              <div className="list-item"><span>SKU</span><strong>{selected.sku}</strong></div>
              <div className="list-item"><span>Producto</span><strong>{selected.name}</strong></div>
              <div className="list-item"><span>Categoría</span><strong>{selected.category}</strong></div>
              <div className="list-item"><span>Precio</span><strong>{money(selected.priceCents)}</strong></div>
              <div className="list-item"><span>Costo</span><strong>{money(selected.costCents)}</strong></div>
              <div className="list-item"><span>Existencias</span><strong>{selected.stockOnHand}</strong></div>
              <div className="list-item"><span>Códigos</span><strong>{selected.barcodes.length ? selected.barcodes.join(", ") : "sin código"}</strong></div>
              <div className="list-item"><span>Estado</span><StatusBadge value={selected.isActive ? "activo" : "inactivo"} /></div>
              <div className="list-item"><span>Actualizado</span><strong>{selected.updatedAtLabel}</strong></div>
              {selected.issues.length ? selected.issues.map((issue) => (
                <div className="alert-strip" key={`${selected.sku}-${issue.type}`} style={{ marginTop: 10 }}>
                  <strong>{issue.label}</strong>
                  <span className="subtle">{issue.detail}</span>
                </div>
              )) : (
                <div className="alert-strip" style={{ marginTop: 10 }}>
                  <strong>Sin incidencias críticas</strong>
                  <span className="subtle">El SKU tiene datos mínimos para operación.</span>
                </div>
              )}
            </div>
          ) : (
            <EmptyState title="Sin producto seleccionado." description="Selecciona un SKU o carga catálogo para ver su ficha." />
          )}
        </article>
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">excepciones</div>
            <h2 className="section-title">Incidencias de catálogo</h2>
            <div className="section-copy">Problemas que conviene resolver antes de compras, recepción, inventario y sincronización.</div>
          </div>
        </div>
        <DataTable
          columns={["Severidad", "SKU", "Producto", "Tipo", "Detalle", "Acción"]}
          rows={workspace.exceptions.map((issue) => ({
            Severidad: issue.severity,
            SKU: issue.sku,
            Producto: issue.productName,
            Tipo: issue.label,
            Detalle: issue.detail,
            Acción: issue.recommendedAction
          }))}
          emptyMessage="No hay incidencias con los filtros actuales."
        />
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <div className="kicker">estado honesto</div>
            <h2 className="section-title">Notas de implementación I02</h2>
          </div>
        </div>
        <div className="list">
          <div className="list-item"><span>Alcance</span><strong>Catálogo PC, SKUs, códigos, excepciones y detalle.</strong></div>
          <div className="list-item"><span>No toca</span><strong>Tablet, kernel compartido ni contratos compartidos.</strong></div>
          <div className="list-item"><span>Persistencia</span><strong>{workspace.meta.persistence}</strong></div>
        </div>
      </section>
    </AppShell>
  );
}
