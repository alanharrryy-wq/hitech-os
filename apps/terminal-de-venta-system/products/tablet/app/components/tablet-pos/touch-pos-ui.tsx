"use client";

import { type FormEvent, type ReactNode, useEffect, useMemo, useState } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { tabletVisibleLabels } from "@/lib/i18n/tablet-visible-labels";
import styles from "./touch-pos.module.css";

type ApiOk<T> = { ok: true; data: T; meta: Record<string, unknown> };
type ApiFail = { ok: false; code: string; message: string; details: Record<string, unknown> };
type ApiResponse<T> = ApiOk<T> | ApiFail;
type UiState = "idle" | "loading" | "ready" | "empty" | "error" | "success";

type PosProduct = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category?: string;
  barcode?: string | null;
  barcodes?: string[];
  priceCents: number;
  stockOnHand: number;
  lowStockThreshold?: number;
  isActive: boolean;
};

type CartLine = {
  product: PosProduct;
  qty: number;
};

type CompletedSale = {
  saleId: string;
  folio: string;
  businessId: string;
  terminalId: string;
  cashier: string;
  totalCents: number;
  status: string;
  createdAt: string;
  lines: Array<{ productId: string; sku: string; productName: string; qty: number; totalCents: number }>;
  events: Array<{ topic: string }>;
};

type TodaySummary = {
  date: string;
  salesCount: number;
  ticketsClosed: number;
  totalCents: number;
  averageTicketCents: number;
  unitsSold: number;
  topProducts: Array<{ productId: string; sku: string; name: string; qty: number; totalCents: number }>;
};

type OperationalReport = {
  date: string;
  runtime?: Record<string, unknown>;
  salesCount: number;
  completedSalesCount: number;
  grossTotalCents: number;
  netTotalCents: number;
  totalUnitsSold: number;
  lowStockCount: number;
  pendingOutboxCount: number;
  failedOutboxCount: number;
  outboxCounts?: Record<string, number>;
  recentMovementsCount: number;
};

type OutboxEvent = {
  id: string;
  eventId: string;
  businessId: string;
  topic: string;
  aggregateId: string;
  status: string;
  attempts: number;
  createdAt: string;
  sentAt: string | null;
  lastError: string | null;
};

const ERROR_MESSAGES: Record<string, string> = {
  EMPTY_CART: "El ticket está vacío.",
  INVALID_QUANTITY: "La cantidad no es válida.",
  PRODUCT_NOT_FOUND: "No encontramos ese producto.",
  PRODUCT_INACTIVE: "Este producto está inactivo.",
  INSUFFICIENT_STOCK: "Existencias insuficientes para este producto.",
  TERMINAL_NOT_FOUND: "No se encontró la terminal configurada.",
  NETWORK_UNAVAILABLE: "No hay conexión disponible. La venta local puede continuar si el modo lo permite.",
  SYNC_PENDING: "Hay eventos pendientes de sincronizar.",
  BUSINESS_NOT_FOUND: "No hay negocio local configurado para vender.",
  ENGINE_INVARIANT_FAILED: "El motor detectó una inconsistencia y no cerró la venta."
};


function formatMoney(cents: number | null | undefined) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format((cents ?? 0) / 100);
}

function friendlyError(error: unknown) {
  if (!error) return "Ocurrió un problema al procesar la operación.";
  if (typeof error === "string") return ERROR_MESSAGES[error] ?? error;
  if (typeof error === "object" && "code" in error) {
    const apiError = error as ApiFail;
    return ERROR_MESSAGES[apiError.code] ?? apiError.message ?? "Ocurrió un problema al procesar la operación.";
  }
  if (error instanceof Error) return error.message;
  return "Ocurrió un problema al procesar la operación.";
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<ApiOk<T>> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {})
    }
  });
  const payload = (await response.json()) as ApiResponse<T>;
  if (!payload.ok) throw payload;
  return payload;
}

function useOnlineStatus() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    setOnline(navigator.onLine);
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return online;
}

function statusTone(value: string): "ok" | "warn" | "danger" | "neutral" {
  const normalized = value.toLowerCase();
  if (normalized === "failed" || normalized === "conflict" || normalized === "error") return "danger";
  if (normalized === "pending" || normalized === "sync_pending" || normalized === "offline") return "warn";
  if (normalized === "sent" || normalized === "acked" || normalized === "ready" || normalized === "success") return "ok";
  return "neutral";
}

export function StatusPill({ tone = "neutral", children }: { tone?: "ok" | "warn" | "danger" | "neutral"; children: ReactNode }) {
  return <span className={[styles.statusPill, styles[`status_${tone}`]].join(" ")}>{children}</span>;
}

export function OperationalError({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <div className={styles.operationalError} role="alert">
      <PrismaIcon name="bell" size={18} />
      <span>{friendlyError(error)}</span>
    </div>
  );
}

function AppChrome({
  currentPath,
  title,
  subtitle,
  status,
  children
}: {
  currentPath: string;
  title: string;
  subtitle: string;
  status?: ReactNode;
  children: ReactNode;
}) {
  return (
    <PrismaTabletShellUnified currentPath={currentPath} title={title} subtitle={subtitle} status={status}>
      {children}
    </PrismaTabletShellUnified>
  );
}

export function RuntimeStatus({
  report,
  state
}: {
  report?: OperationalReport | null;
  state?: UiState;
}) {
  const online = useOnlineStatus();
  const runtime = typeof report?.runtime?.runtimeMode === "string" ? report.runtime.runtimeMode : "standalone";
  const pending = report?.pendingOutboxCount ?? 0;
  const failed = report?.failedOutboxCount ?? 0;

  return (
    <div className={styles.runtimeBar} aria-label="Estado de operación">
      <StatusPill tone={online ? "ok" : "warn"}>{online ? "Red disponible" : "Sin red"}</StatusPill>
      <StatusPill tone="ok">{runtime === "standalone" ? tabletVisibleLabels.status.localMode : runtime}</StatusPill>
      <StatusPill tone={pending ? "warn" : "ok"}>{pending} pendientes</StatusPill>
      <StatusPill tone={failed ? "danger" : "ok"}>{failed} con error</StatusPill>
      {state === "loading" ? <StatusPill tone="neutral">cargando</StatusPill> : null}
    </div>
  );
}

export function TouchProductSearch({
  query,
  setQuery,
  loading,
  error,
  onSearch,
  onResolve,
  onClear
}: {
  query: string;
  setQuery: (value: string) => void;
  loading: boolean;
  error: unknown;
  onSearch: () => void;
  onResolve: () => void;
  onClear: () => void;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className={styles.searchBlock} onSubmit={submit}>
      <label className={styles.searchInput}>
        <PrismaIcon name="search" size={22} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar producto, SKU o código..." type="search" />
      </label>
      <button className={styles.scanButton} type="button" onClick={onResolve} disabled={loading || !query.trim()}>
        <PrismaIcon name="scan" size={20} />
        <span>Resolver código</span>
      </button>
      <button className={styles.secondaryButton} type="button" onClick={onClear} disabled={loading}>
        Limpiar
      </button>
      {error ? <OperationalError error={error} /> : null}
    </form>
  );
}

export function TouchProductList({
  products,
  state,
  error,
  onAdd,
  actionLabel = tabletVisibleLabels.actions.add
}: {
  products: PosProduct[];
  state: UiState;
  error: unknown;
  onAdd?: (product: PosProduct) => void;
  actionLabel?: string;
}) {
  if (state === "loading") {
    return <StatePanel icon="package" title="Cargando catálogo local" description="Leyendo productos desde la base local de Tablet." />;
  }
  if (state === "error") {
    return <StatePanel icon="bell" title="No se pudo leer el catálogo" description={friendlyError(error)} tone="danger" />;
  }
  if (!products.length) {
    return <StatePanel icon="package" title="No hay productos cargados en la base local" description="La venta queda lista en cuanto exista catálogo local." />;
  }

  return (
    <section className={styles.productGrid} aria-label="Productos encontrados">
      {products.map((product) => (
        <article key={product.id} className={styles.productCard}>
          <div className={styles.productFigure}>
            <PrismaIcon name="package" size={30} />
          </div>
          <div className={styles.productInfo}>
            <strong>{product.name}</strong>
            <span>{product.sku} {product.barcode ? `· ${product.barcode}` : ""}</span>
            <div className={styles.productSignals}>
              <StatusPill tone={product.isActive ? "ok" : "danger"}>{product.isActive ? "activo" : "inactivo"}</StatusPill>
              <StatusPill tone={product.stockOnHand <= (product.lowStockThreshold ?? 5) ? "warn" : "neutral"}>{product.stockOnHand} existencias</StatusPill>
            </div>
          </div>
          <footer className={styles.productFooter}>
            <span>{formatMoney(product.priceCents)}</span>
            {onAdd ? (
              <button type="button" onClick={() => onAdd(product)} disabled={!product.isActive}>
                <PrismaIcon name="plus" size={18} />
                {actionLabel}
              </button>
            ) : (
              <StatusPill tone="neutral">Consulta</StatusPill>
            )}
          </footer>
        </article>
      ))}
    </section>
  );
}

export function TouchCart({
  lines,
  paymentMethod,
  saleState,
  saleError,
  onPaymentMethod,
  onIncrement,
  onDecrement,
  onRemove,
  onClear,
  onCheckout
}: {
  lines: CartLine[];
  paymentMethod: string;
  saleState: UiState;
  saleError: unknown;
  onPaymentMethod: (value: string) => void;
  onIncrement: (productId: string) => void;
  onDecrement: (productId: string) => void;
  onRemove: (productId: string) => void;
  onClear: () => void;
  onCheckout: () => void;
}) {
  const totalCents = useMemo(() => lines.reduce((sum, line) => sum + line.product.priceCents * line.qty, 0), [lines]);
  const totalQty = useMemo(() => lines.reduce((sum, line) => sum + line.qty, 0), [lines]);

  return (
    <aside className={styles.cartPanel} aria-label="Ticket actual">
      <header className={styles.panelHeader}>
        <div>
          <span>ticket activo</span>
          <h2>Carrito</h2>
        </div>
        <StatusPill tone={lines.length ? "ok" : "neutral"}>{totalQty} piezas</StatusPill>
      </header>

      <div className={styles.cartLines}>
        {!lines.length ? (
          <StatePanel icon="cart" title="Ticket vacío" description="Busca o escanea un producto para iniciar la venta." />
        ) : (
          lines.map((line) => (
            <article key={line.product.id} className={styles.cartLine}>
              <div>
                <strong>{line.product.name}</strong>
                <span>{line.product.sku} · {formatMoney(line.product.priceCents)}</span>
              </div>
              <div className={styles.stepper}>
                <button type="button" aria-label="Restar" onClick={() => onDecrement(line.product.id)}>
                  <PrismaIcon name="minus" size={16} />
                </button>
                <strong>{line.qty}</strong>
                <button type="button" aria-label="Sumar" onClick={() => onIncrement(line.product.id)}>
                  <PrismaIcon name="plus" size={16} />
                </button>
              </div>
              <strong className={styles.lineTotal}>{formatMoney(line.product.priceCents * line.qty)}</strong>
              <button className={styles.iconOnlyButton} type="button" aria-label="Quitar línea" onClick={() => onRemove(line.product.id)}>
                <PrismaIcon name="trash" size={17} />
              </button>
            </article>
          ))
        )}
      </div>

      <div className={styles.paymentRow} aria-label="Método de pago">
        {[
          ["cash", "Efectivo"],
          ["card", "Tarjeta"],
          ["mixed", "Mixto"]
        ].map(([value, label]) => (
          <button key={value} className={paymentMethod === value ? styles.paymentActive : styles.paymentButton} type="button" onClick={() => onPaymentMethod(value)}>
            {label}
          </button>
        ))}
      </div>

      <div className={styles.totalBox}>
        <span>Total</span>
        <strong>{formatMoney(totalCents)}</strong>
      </div>

      <CheckoutButton disabled={!lines.length || saleState === "loading"} loading={saleState === "loading"} onClick={onCheckout} />
      <button className={styles.secondaryWideButton} type="button" onClick={onClear} disabled={!lines.length || saleState === "loading"}>
        Limpiar ticket
      </button>
      {saleError ? <OperationalError error={saleError} /> : null}
    </aside>
  );
}

export function CheckoutButton({ disabled, loading, onClick }: { disabled: boolean; loading: boolean; onClick: () => void }) {
  return (
    <button className={styles.checkoutButton} type="button" disabled={disabled} onClick={onClick}>
      <span>{loading ? "Cerrando venta..." : "COBRAR"}</span>
      <strong>F2</strong>
    </button>
  );
}

export function TicketSummary({ sale, onReset }: { sale: CompletedSale | null; onReset: () => void }) {
  if (!sale) return null;
  return (
    <section className={styles.ticketSummary} aria-label="Ticket cerrado">
      <div>
        <span>venta cerrada</span>
        <h2>{sale.folio}</h2>
        <p>{sale.lines.length} líneas · {sale.events.length} eventos locales</p>
      </div>
      <strong>{formatMoney(sale.totalCents)}</strong>
      <button className={styles.secondaryButton} type="button" onClick={onReset}>
        Nueva venta
      </button>
    </section>
  );
}

export function OutboxMiniPanel({ report, state }: { report: OperationalReport | null; state: UiState }) {
  return (
    <section className={styles.miniPanel} aria-label="Pendientes por enviar">
      <div>
        <span>pendientes por enviar</span>
        <strong>{state === "loading" ? "..." : `${report?.pendingOutboxCount ?? 0} pendientes`}</strong>
      </div>
      <StatusPill tone={(report?.failedOutboxCount ?? 0) > 0 ? "danger" : "ok"}>{report?.failedOutboxCount ?? 0} fallidos</StatusPill>
      <a href="/events/outbox">Ver pendientes</a>
    </section>
  );
}

function StatePanel({
  title,
  description,
  icon,
  tone = "neutral"
}: {
  title: string;
  description: string;
  icon: PrismaIconName;
  tone?: "neutral" | "danger";
}) {
  return (
    <div className={[styles.statePanel, tone === "danger" ? styles.stateDanger : ""].join(" ")}>
      <PrismaIcon name={icon} size={26} />
      <strong>{title}</strong>
      <span>{description}</span>
    </div>
  );
}

export function TouchPosApp({ compatibility = false }: { compatibility?: boolean }) {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [productState, setProductState] = useState<UiState>("idle");
  const [productError, setProductError] = useState<unknown>(null);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [saleState, setSaleState] = useState<UiState>("idle");
  const [saleError, setSaleError] = useState<unknown>(null);
  const [lastSale, setLastSale] = useState<CompletedSale | null>(null);
  const [report, setReport] = useState<OperationalReport | null>(null);
  const [reportState, setReportState] = useState<UiState>("idle");

  async function loadProducts(nextQuery = query) {
    setProductState("loading");
    setProductError(null);
    try {
      const response = await requestJson<{ products: PosProduct[]; count: number }>(`/api/pos/products/search?q=${encodeURIComponent(nextQuery)}`);
      setProducts(response.data.products);
      setProductState(response.data.products.length ? "ready" : "empty");
    } catch (error) {
      setProductError(error);
      setProductState("error");
    }
  }

  async function resolveCode() {
    const code = query.trim();
    if (!code) return;
    setProductState("loading");
    setProductError(null);
    try {
      const response = await requestJson<{ product: PosProduct }>(`/api/pos/products/resolve?code=${encodeURIComponent(code)}`);
      setProducts([response.data.product]);
      setProductState("ready");
      addProduct(response.data.product);
    } catch (error) {
      setProductError(error);
      setProductState("error");
    }
  }

  async function loadReport() {
    setReportState("loading");
    try {
      const response = await requestJson<{ report: OperationalReport }>("/api/pos/reports/operational-today");
      setReport(response.data.report);
      setReportState("ready");
    } catch {
      setReportState("error");
    }
  }

  function addProduct(product: PosProduct) {
    setLastSale(null);
    setCart((current) => {
      const existing = current.find((line) => line.product.id === product.id);
      if (existing) {
        return current.map((line) => (line.product.id === product.id ? { ...line, qty: line.qty + 1 } : line));
      }
      return [...current, { product, qty: 1 }];
    });
  }

  function increment(productId: string) {
    setCart((current) => current.map((line) => (line.product.id === productId ? { ...line, qty: line.qty + 1 } : line)));
  }

  function decrement(productId: string) {
    setCart((current) =>
      current.flatMap((line) => {
        if (line.product.id !== productId) return [line];
        if (line.qty <= 1) return [];
        return [{ ...line, qty: line.qty - 1 }];
      })
    );
  }

  function makeClientRequestId() {
    return typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `sale_${Date.now()}_${Math.random().toString(36).slice(2)}`;
  }

  async function completeSale() {
    if (!cart.length) {
      setSaleError("EMPTY_CART");
      return;
    }
    setSaleState("loading");
    setSaleError(null);
    try {
      const response = await requestJson<{ sale: CompletedSale }>("/api/pos/sales/complete", {
        method: "POST",
        body: JSON.stringify({
          clientRequestId: makeClientRequestId(),
          paymentMethod,
          lines: cart.map((line) => ({ productId: line.product.id, qty: line.qty }))
        })
      });
      setLastSale(response.data.sale);
      setCart([]);
      setSaleState("success");
      await Promise.all([loadProducts(query), loadReport()]);
    } catch (error) {
      setSaleError(error);
      setSaleState("error");
    }
  }

  useEffect(() => {
    void loadProducts("");
    void loadReport();
  }, []);

  return (
    <AppChrome
      currentPath={compatibility ? "/checkout" : "/pos"}
      title={compatibility ? "Cobro" : tabletVisibleLabels.actions.sell}
      subtitle="Venta local, ticket, existencias y pendientes desde la Tablet."
      status={<RuntimeStatus report={report} state={reportState} />}
    >
      <div className={styles.posWorkspace}>
        <section className={styles.catalogPanel}>
          <TouchProductSearch
            query={query}
            setQuery={setQuery}
            loading={productState === "loading"}
            error={productError}
            onSearch={() => void loadProducts(query)}
            onResolve={() => void resolveCode()}
            onClear={() => {
              setQuery("");
              void loadProducts("");
            }}
          />
          <TouchProductList products={products} state={productState} error={productError} onAdd={addProduct} />
        </section>

        <div className={styles.rightRail}>
          <OutboxMiniPanel report={report} state={reportState} />
          <TicketSummary sale={lastSale} onReset={() => setLastSale(null)} />
          <TouchCart
            lines={cart}
            paymentMethod={paymentMethod}
            saleState={saleState}
            saleError={saleError}
            onPaymentMethod={setPaymentMethod}
            onIncrement={increment}
            onDecrement={decrement}
            onRemove={(productId) => setCart((current) => current.filter((line) => line.product.id !== productId))}
            onClear={() => setCart([])}
            onCheckout={() => void completeSale()}
          />
        </div>
      </div>
    </AppChrome>
  );
}

export function CatalogScreen() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [state, setState] = useState<UiState>("idle");
  const [error, setError] = useState<unknown>(null);

  async function load(nextQuery = query) {
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<{ products: PosProduct[]; count: number }>(`/api/pos/products/search?q=${encodeURIComponent(nextQuery)}&includeInactive=true`);
      setProducts(response.data.products);
      setState(response.data.products.length ? "ready" : "empty");
    } catch (caught) {
      setError(caught);
      setState("error");
    }
  }

  useEffect(() => {
    void load("");
  }, []);

  return (
    <AppChrome currentPath="/catalog" title="Catálogo" subtitle="Productos disponibles para vender en Tablet." status={<RuntimeStatus state={state} />}>
      <section className={styles.singleColumn}>
        <TouchProductSearch query={query} setQuery={setQuery} loading={state === "loading"} error={error} onSearch={() => void load(query)} onResolve={() => void load(query)} onClear={() => { setQuery(""); void load(""); }} />
        <TouchProductList products={products} state={state} error={error} />
      </section>
    </AppChrome>
  );
}

export function SalesTodayScreen() {
  const [summary, setSummary] = useState<TodaySummary | null>(null);
  const [report, setReport] = useState<OperationalReport | null>(null);
  const [state, setState] = useState<UiState>("loading");
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    async function load() {
      setState("loading");
      try {
        const [summaryResponse, reportResponse] = await Promise.all([
          requestJson<{ summary: TodaySummary }>("/api/pos/sales/today"),
          requestJson<{ report: OperationalReport }>("/api/pos/reports/operational-today")
        ]);
        setSummary(summaryResponse.data.summary);
        setReport(reportResponse.data.report);
        setState("ready");
      } catch (caught) {
        setError(caught);
        setState("error");
      }
    }
    void load();
  }, []);

  return (
    <AppChrome currentPath="/sales/today" title="Ventas de hoy" subtitle="Corte operativo local de la Tablet." status={<RuntimeStatus report={report} state={state} />}>
      <section className={styles.summaryGrid}>
        <Metric label="Ventas" value={String(summary?.salesCount ?? 0)} note="tickets locales" icon="receipt" />
        <Metric label="Total" value={formatMoney(summary?.totalCents)} note="neto local" icon="wallet" />
        <Metric label="Unidades" value={String(summary?.unitsSold ?? 0)} note="piezas vendidas" icon="package" />
        <Metric label="Ticket promedio" value={formatMoney(summary?.averageTicketCents)} note={summary?.date ?? "hoy"} icon="chart" />
      </section>
      {state === "error" ? <OperationalError error={error} /> : null}
      {!summary?.topProducts?.length && state !== "error" ? <StatePanel icon="receipt" title="Sin ventas registradas hoy" description="Cuando se cierre una venta local, aparecerá aquí." /> : null}
      {summary?.topProducts?.length ? (
        <DataPanel title="Productos vendidos">
          {summary.topProducts.map((product) => (
            <DataRow key={product.productId} title={product.name} detail={`${product.sku} · ${product.qty} uds`} aside={formatMoney(product.totalCents)} />
          ))}
        </DataPanel>
      ) : null}
    </AppChrome>
  );
}

export function LowStockScreen() {
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [state, setState] = useState<UiState>("loading");
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await requestJson<{ products: PosProduct[]; count: number }>("/api/pos/inventory/low-stock");
        setProducts(response.data.products);
        setState(response.data.products.length ? "ready" : "empty");
      } catch (caught) {
        setError(caught);
        setState("error");
      }
    }
    void load();
  }, []);

  return (
    <AppChrome currentPath="/inventory/low-stock" title="Existencias" subtitle="Productos con pocas piezas o atención local." status={<RuntimeStatus state={state} />}>
      {state === "loading" ? <StatePanel icon="package" title="Leyendo existencias locales" description="Consultando inventario de la Tablet." /> : null}
      {state === "error" ? <OperationalError error={error} /> : null}
      {state === "empty" ? <StatePanel icon="package" title="Sin alertas de existencias bajas" description="No hay productos bajo el umbral actual." /> : null}
      {products.length ? (
        <DataPanel title="Productos en umbral">
          {products.map((product) => (
            <DataRow key={product.id} title={product.name} detail={`${product.sku} · umbral ${product.lowStockThreshold ?? 5}`} aside={`${product.stockOnHand} pzas`} tone="warn" />
          ))}
        </DataPanel>
      ) : null}
    </AppChrome>
  );
}

export function OutboxEventsScreen() {
  const [events, setEvents] = useState<OutboxEvent[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [state, setState] = useState<UiState>("loading");
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await requestJson<{ events: OutboxEvent[]; counts: Record<string, number>; count: number }>("/api/pos/events/outbox");
        setEvents(response.data.events);
        setCounts(response.data.counts);
        setState(response.data.events.length ? "ready" : "empty");
      } catch (caught) {
        setError(caught);
        setState("error");
      }
    }
    void load();
  }, []);

  return (
    <AppChrome currentPath="/events/outbox" title="Pendientes por enviar" subtitle="Eventos locales esperando sincronización." status={<RuntimeStatus state={state} />}>
      <section className={styles.summaryGrid}>
        <Metric label="Pendientes" value={String(counts.pending ?? 0)} note="por enviar" icon="chart" />
        <Metric label="Fallidos" value={String(counts.failed ?? 0)} note="requieren atención" icon="bell" />
        <Metric label="ACK" value={String(counts.acked ?? 0)} note="confirmados" icon="receipt" />
        <Metric label="Conflictos" value={String(counts.conflict ?? 0)} note="para PC" icon="settings" />
      </section>
      {state === "error" ? <OperationalError error={error} /> : null}
      {state === "empty" ? <StatePanel icon="chart" title="Sin pendientes por enviar" description="Las ventas locales generarán eventos operativos aquí." /> : null}
      {events.length ? (
        <DataPanel title="Eventos locales">
          {events.map((event) => (
            <DataRow key={event.id} title={event.topic} detail={`${event.aggregateId} · ${new Date(event.createdAt).toLocaleString("es-MX")}`} aside={<StatusPill tone={statusTone(event.status)}>{event.status}</StatusPill>} />
          ))}
        </DataPanel>
      ) : null}
    </AppChrome>
  );
}

export function ExportSettingsScreen() {
  const [status, setStatus] = useState<string | null>(null);
  const endpoints = [
    { label: "Ventas de hoy JSON", href: "/api/pos/export/sales-today?format=json" },
    { label: "Ventas de hoy CSV", href: "/api/pos/export/sales-today?format=csv" },
    { label: "Eventos JSON", href: "/api/pos/export/events?format=json" },
    { label: "Eventos CSV", href: "/api/pos/export/events?format=csv" },
    { label: "Movimientos JSON", href: "/api/pos/export/inventory-movements?format=json" },
    { label: "Movimientos CSV", href: "/api/pos/export/inventory-movements?format=csv" }
  ];

  return (
    <AppChrome currentPath="/settings/export" title="Exportaciones locales" subtitle="Salidas operativas desde la base local de Tablet." status={<RuntimeStatus state={status ? "success" : "ready"} />}>
      <ExportPanel>
        {endpoints.map((endpoint) => (
          <ExportButton key={endpoint.href} label={endpoint.label} href={endpoint.href} onDone={setStatus} />
        ))}
      </ExportPanel>
      {status ? <div className={styles.successLine}>{status}</div> : null}
    </AppChrome>
  );
}

export function ExportPanel({ children }: { children: ReactNode }) {
  return <section className={styles.exportGrid}>{children}</section>;
}

export function ExportButton({ label, href, onDone }: { label: string; href: string; onDone: (message: string) => void }) {
  return (
    <button
      className={styles.exportButton}
      type="button"
      onClick={() => {
        window.open(href, "_blank", "noopener,noreferrer");
        onDone(`${label} solicitado.`);
      }}
    >
      <PrismaIcon name="save" size={22} />
      <span>{label}</span>
    </button>
  );
}

function Metric({ label, value, note, icon }: { label: string; value: string; note: string; icon: PrismaIconName }) {
  return (
    <article className={styles.metricCard}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
      <PrismaIcon name={icon} size={20} />
    </article>
  );
}

function DataPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className={styles.dataPanel}>
      <h2>{title}</h2>
      <div className={styles.dataRows}>{children}</div>
    </section>
  );
}

function DataRow({ title, detail, aside, tone = "neutral" }: { title: string; detail: string; aside: ReactNode; tone?: "neutral" | "warn" | "danger" }) {
  return (
    <article className={[styles.dataRow, tone === "warn" ? styles.rowWarn : tone === "danger" ? styles.rowDanger : ""].join(" ")}>
      <div>
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
      <div>{aside}</div>
    </article>
  );
}
