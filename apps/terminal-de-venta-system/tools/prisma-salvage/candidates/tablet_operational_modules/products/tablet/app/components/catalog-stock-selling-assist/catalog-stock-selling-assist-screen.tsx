"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
import type {
  CatalogStockFilter,
  CatalogStockSearchState,
  CatalogStockSellingAssistMode,
  CatalogStockSellingAssistProduct
} from "@/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-contract";
import { CATALOG_STOCK_SCREEN_COPY } from "@/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-contract";
import {
  buildCatalogStockMetrics,
  buildProductDetailRows,
  buildProductSearchUrl,
  buildStockRiskSummary,
  canSendProductToSale,
  describeProductSignal,
  filterProductsForSellingAssist,
  getBlockedSaleReason,
  getCatalogStockLabel,
  getCatalogStockSignal,
  getCatalogStockTone,
  getProductBarcode
} from "@/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model";
import {
  addSellingAssistProductToCart,
  readSellingAssistCartSummary
} from "@/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff";
import styles from "./catalog-stock-selling-assist.module.css";

type ProductSearchResponse = { products: CatalogStockSellingAssistProduct[]; count: number };

type Props = {
  mode: CatalogStockSellingAssistMode;
};

const FILTERS: Array<{ id: CatalogStockFilter; label: string; description: string }> = [
  { id: "all", label: "Todos", description: "ver catálogo completo" },
  { id: "available", label: "Vendibles", description: "listos para mandar al carrito" },
  { id: "low_stock", label: "Stock bajo", description: "vender con ojo de halcón" },
  { id: "out_of_stock", label: "Sin stock", description: "bloqueados para venta" },
  { id: "inactive", label: "Inactivos", description: "no se mandan al carrito" }
];

function statusText(state: CatalogStockSearchState, products: CatalogStockSellingAssistProduct[]) {
  if (state === "loading") return "Leyendo productos";
  if (state === "offline") return "Sin conexión visible";
  if (state === "error") return "Revisar catálogo";
  if (!products.length) return "Sin productos cargados";
  const blocked = products.filter((product) => !canSendProductToSale(product)).length;
  return blocked ? `${blocked} bloqueo(s)` : "Listo para vender";
}

function statusTone(state: CatalogStockSearchState, products: CatalogStockSellingAssistProduct[]) {
  if (state === "error" || state === "offline") return "danger" as const;
  if (state === "loading") return "warn" as const;
  if (products.some((product) => getCatalogStockSignal(product) === "low_stock")) return "warn" as const;
  return "ok" as const;
}

function visibleApiError(error: unknown) {
  if (!error) return "";
  if (typeof error === "object" && error && "message" in error) return String((error as { message?: unknown }).message ?? "Error de lectura.");
  if (typeof error === "object" && error && "code" in error) return String((error as { code?: unknown }).code ?? "Error de lectura.");
  return "No se pudo leer el catálogo local.";
}

function productToneClass(product: CatalogStockSellingAssistProduct) {
  const tone = getCatalogStockTone(getCatalogStockSignal(product));
  if (tone === "ok") return styles.toneOk;
  if (tone === "warn") return styles.toneWarn;
  if (tone === "danger") return styles.toneDanger;
  return styles.toneNeutral;
}

function ProductStatusBadge({ product }: { product: CatalogStockSellingAssistProduct }) {
  const signal = getCatalogStockSignal(product);
  return <span className={[styles.statusBadge, productToneClass(product)].join(" ")}>{getCatalogStockLabel(signal)}</span>;
}

function OfflineStrip({ online, cachedCount }: { online: boolean; cachedCount: number }) {
  return (
    <div className={online ? styles.onlineStrip : styles.offlineStrip} role={online ? "status" : "alert"} data-prisma-component="OfflineState">
      <PrismaIcon name={online ? "terminal" : "bell"} size={18} />
      <span>
        {online
          ? `Conexión visible. ${cachedCount} producto(s) cargados para operación.`
          : `Sin conexión visible. Puedes revisar lo ya cargado y mandar productos vendibles al carrito local.`}
      </span>
    </div>
  );
}

function MetricCard({ metric }: { metric: ReturnType<typeof buildCatalogStockMetrics>[number] }) {
  const toneClass = metric.tone === "ok" ? styles.metricOk : metric.tone === "warn" ? styles.metricWarn : metric.tone === "danger" ? styles.metricDanger : styles.metricNeutral;
  return (
    <article className={[styles.metricCard, toneClass].join(" ")}>
      <span>{metric.label}</span>
      <strong>{metric.value}</strong>
      <small>{metric.note}</small>
    </article>
  );
}

function ProductRow({
  product,
  selected,
  onSelect,
  onAdd
}: {
  product: CatalogStockSellingAssistProduct;
  selected: boolean;
  onSelect: () => void;
  onAdd: () => void;
}) {
  const barcode = getProductBarcode(product);
  const blockedReason = getBlockedSaleReason(product);
  return (
    <article className={[styles.productRow, selected ? styles.productRowSelected : ""].join(" ")} data-prisma-component="CatalogStockProductRow">
      <button type="button" className={styles.productMainButton} onClick={onSelect} aria-pressed={selected}>
        <span className={[styles.productGlyph, productToneClass(product)].join(" ")} aria-hidden="true">
          {product.name.slice(0, 2).toUpperCase()}
        </span>
        <span className={styles.productTextBlock}>
          <strong>{product.name}</strong>
          <small>{product.sku}{barcode ? ` · ${barcode}` : " · Sin código"}</small>
        </span>
      </button>
      <span className={styles.priceCell}>{formatMoney(product.priceCents)}</span>
      <span className={styles.stockCell}>{product.stockOnHand ?? 0} uds</span>
      <ProductStatusBadge product={product} />
      <button
        type="button"
        className={styles.rowAddButton}
        onClick={onAdd}
        disabled={!canSendProductToSale(product)}
        title={blockedReason || "Agregar a venta"}
      >
        <PrismaIcon name="plus" size={16} />
        Agregar
      </button>
    </article>
  );
}

function ProductDetailPanel({
  product,
  onAdd,
  cartNotice
}: {
  product: CatalogStockSellingAssistProduct | null;
  onAdd: (product: CatalogStockSellingAssistProduct) => void;
  cartNotice: string;
}) {
  if (!product) {
    return (
      <aside className={styles.detailPanel} aria-label="Detalle de producto">
        <div className={styles.detailEmpty}>
          <PrismaIcon name="package" size={26} />
          <strong>Selecciona un producto</strong>
          <span>Verás precio, SKU, código, existencia y si puede ir directo a venta.</span>
        </div>
      </aside>
    );
  }
  const canAdd = canSendProductToSale(product);
  const blockedReason = getBlockedSaleReason(product);
  return (
    <aside className={styles.detailPanel} aria-label="Detalle ligero de producto" data-prisma-component="ProductDetail">
      <div className={styles.detailHeader}>
        <span className={styles.detailKicker}>Detalle ligero</span>
        <ProductStatusBadge product={product} />
      </div>
      <h2>{product.name}</h2>
      <p>{describeProductSignal(product)}</p>
      <dl className={styles.detailGrid}>
        {buildProductDetailRows(product).map((row) => (
          <div key={row.label}>
            <dt>{row.label}</dt>
            <dd>{row.value}</dd>
          </div>
        ))}
      </dl>
      {blockedReason ? <div className={styles.blockedMessage} role="alert">{blockedReason}</div> : null}
      {cartNotice ? <div className={styles.cartNotice} role="status">{cartNotice}</div> : null}
      <div className={styles.detailActions}>
        <button type="button" className={styles.primaryAction} onClick={() => onAdd(product)} disabled={!canAdd}>
          <PrismaIcon name="cart" size={18} />
          Agregar a venta
        </button>
        <Link className={styles.secondaryAction} href="/pos">Ir a /pos</Link>
      </div>
    </aside>
  );
}

export function CatalogStockSellingAssistScreen({ mode }: Props) {
  const copy = CATALOG_STOCK_SCREEN_COPY[mode];
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<CatalogStockFilter>(mode === "stock" ? "low_stock" : "all");
  const [products, setProducts] = useState<CatalogStockSellingAssistProduct[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [state, setState] = useState<CatalogStockSearchState>("idle");
  const [error, setError] = useState<unknown>(null);
  const [online, setOnline] = useState(true);
  const [cartNotice, setCartNotice] = useState("");
  const [cartSummary, setCartSummary] = useState({ lines: 0, units: 0, hasCart: false });

  const metrics = useMemo(() => buildCatalogStockMetrics(products), [products]);
  const visibleProducts = useMemo(() => filterProductsForSellingAssist(products, query, filter, mode), [products, query, filter, mode]);
  const selectedProduct = useMemo(() => {
    const bySelected = products.find((product) => product.id === selectedId);
    return bySelected ?? visibleProducts[0] ?? null;
  }, [products, selectedId, visibleProducts]);
  const riskSummary = useMemo(() => buildStockRiskSummary(products), [products]);

  async function loadProducts(nextQuery = query) {
    if (typeof navigator !== "undefined" && !navigator.onLine && products.length) {
      setState("offline");
      return;
    }
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<ProductSearchResponse>(buildProductSearchUrl(nextQuery, true));
      const nextProducts = response.data.products;
      setProducts(nextProducts);
      setSelectedId((current) => current || nextProducts[0]?.id || "");
      setState(nextProducts.length ? "ready" : "empty");
    } catch (caught) {
      setError(caught);
      setState(products.length ? "offline" : "error");
    }
  }

  async function resolveCode() {
    const code = query.trim();
    if (!code) return;
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<{ product: CatalogStockSellingAssistProduct }>(`/api/pos/products/resolve?code=${encodeURIComponent(code)}`);
      const product = response.data.product;
      setProducts((current) => {
        const withoutDuplicate = current.filter((item) => item.id !== product.id);
        return [product, ...withoutDuplicate];
      });
      setSelectedId(product.id);
      setState("ready");
    } catch (caught) {
      setError(caught);
      setState(products.length ? "ready" : "error");
    }
  }

  function addToSale(product: CatalogStockSellingAssistProduct) {
    const result = addSellingAssistProductToCart(product);
    if (result.ok) {
      setCartNotice(result.message);
      setCartSummary(readSellingAssistCartSummary());
      setSelectedId(product.id);
      return;
    }
    setCartNotice(result.message);
    setSelectedId(product.id);
  }

  useEffect(() => {
    setOnline(typeof navigator === "undefined" ? true : navigator.onLine);
    setCartSummary(readSellingAssistCartSummary());
    void loadProducts("");
    function handleOnline() { setOnline(true); }
    function handleOffline() { setOnline(false); setState((current) => (products.length ? "offline" : current)); }
    function handleCart() { setCartSummary(readSellingAssistCartSummary()); }
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    window.addEventListener("prisma:tablet-cart-updated", handleCart as EventListener);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("prisma:tablet-cart-updated", handleCart as EventListener);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <PrismaTabletShellUnified
      currentPath={copy.currentPath}
      title={copy.title}
      subtitle={copy.subtitle}
      status={<TabletShellStatusPill tone={statusTone(state, products)}>{statusText(state, products)}</TabletShellStatusPill>}
    >
      <div className={styles.screen} data-prisma-screen={`catalog-stock-selling-assist-${mode}`}>
        <OfflineStrip online={online} cachedCount={products.length} />

        <section className={styles.heroCard}>
          <div>
            <span className={styles.kicker}>{copy.kicker}</span>
            <h1>{mode === "stock" ? "Del anaquel al carrito sin perder el paso" : "Catálogo conectado al carrito real"}</h1>
            <p>{riskSummary}</p>
          </div>
          <div className={styles.cartChip} aria-label="Carrito activo">
            <PrismaIcon name="cart" size={20} />
            <span>{cartSummary.hasCart ? `${cartSummary.units} pieza(s) en venta` : "Carrito vacío"}</span>
            <Link href="/pos">Abrir venta</Link>
          </div>
        </section>

        <section className={styles.metricGrid} aria-label="Resumen catálogo y existencias">
          {metrics.map((metric) => <MetricCard key={metric.id} metric={metric} />)}
        </section>

        <section className={styles.workspace}>
          <div className={styles.mainPanel}>
            <form className={styles.searchPanel} onSubmit={(event) => { event.preventDefault(); void loadProducts(query); }}>
              <label>
                <span>Búsqueda operativa</span>
                <div className={styles.searchInputWrap}>
                  <PrismaIcon name="search" size={20} />
                  <input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder={copy.searchPlaceholder}
                    type="search"
                  />
                </div>
              </label>
              <div className={styles.searchActions}>
                <button type="submit" className={styles.primaryAction} disabled={state === "loading"}>{state === "loading" ? "Buscando..." : "Buscar"}</button>
                <button type="button" className={styles.secondaryAction} onClick={() => void resolveCode()} disabled={!query.trim() || state === "loading"}>Resolver código</button>
                <button type="button" className={styles.ghostAction} onClick={() => { setQuery(""); void loadProducts(""); }}>Limpiar</button>
              </div>
            </form>

            <nav className={styles.filterRail} aria-label="Filtros de catálogo y stock">
              {FILTERS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={filter === item.id ? styles.filterActive : styles.filterButton}
                  onClick={() => setFilter(item.id)}
                  aria-pressed={filter === item.id}
                >
                  <strong>{item.label}</strong>
                  <span>{item.description}</span>
                </button>
              ))}
            </nav>

            {error ? <div className={styles.errorBox} role="alert">{visibleApiError(error)}</div> : null}

            <div className={styles.productList} aria-label="Productos encontrados">
              {state === "loading" ? (
                <div className={styles.statePanel}><PrismaIcon name="package" size={24} /><strong>Leyendo catálogo local</strong><span>Consultando productos y existencias.</span></div>
              ) : visibleProducts.length ? (
                visibleProducts.map((product) => (
                  <ProductRow
                    key={product.id}
                    product={product}
                    selected={selectedProduct?.id === product.id}
                    onSelect={() => setSelectedId(product.id)}
                    onAdd={() => addToSale(product)}
                  />
                ))
              ) : (
                <div className={styles.statePanel} data-prisma-component="EmptyState">
                  <PrismaIcon name="package" size={24} />
                  <strong>{copy.emptyTitle}</strong>
                  <span>{copy.emptyDescription}</span>
                </div>
              )}
            </div>
          </div>

          <ProductDetailPanel product={selectedProduct} onAdd={addToSale} cartNotice={cartNotice} />
        </section>
      </div>
    </PrismaTabletShellUnified>
  );
}
