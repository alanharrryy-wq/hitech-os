import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const failures = [];

function read(rel) {
  const file = resolve(root, rel);
  if (!existsSync(file)) {
    failures.push(`missing ${rel}`);
    return "";
  }
  return readFileSync(file, "utf8");
}

function check(label, condition, rel = "") {
  if (!condition) failures.push(rel ? `${label} (${rel})` : label);
}

function hasAll(rel, needles) {
  const text = read(rel);
  for (const needle of needles) check(`missing ${needle}`, text.includes(needle), rel);
  return text;
}

function countNeedle(text, needle) {
  return text.split(needle).length - 1;
}

hasAll("app/pos/page.tsx", ["SellingWorkspace", "getTabletRuntimeSnapshot", "force-dynamic"]);
hasAll("app/checkout/page.tsx", ["CheckoutWorkspace", "getTabletRuntimeSnapshot", "force-dynamic"]);

const posScreen = hasAll("components/pos/pos-screen.tsx", [
  "PosProductSearch",
  "PosProductList",
  "PosTicketPanel",
  "PosTerminalSurface",
  "PosCommandDock",
  "validateCartForCheckout",
  "writeCartToStorage",
  "clearCartStorage()",
  "onIncrement",
  "onDecrement",
  "onRemove",
  "onClear",
  "onCheckout",
  'visualSurface="tablet-pos-nocturne"'
]);
check("POS conserva una sola superficie terminal visible por estado", countNeedle(posScreen, "<PosTerminalSurface") === countNeedle(posScreen, "</PosTerminalSurface>"), "components/pos/pos-screen.tsx");
check("POS gobierna el dock durante checkout", posScreen.includes("showBottomDock={!checkoutBackdrop}"), "components/pos/pos-screen.tsx");

hasAll("components/pos/pos-product-search.tsx", [
  "type=\"search\"",
  "onSearch",
  "onClear",
  "Buscar",
  "Buscar producto o escanear código",
  "Limpiar"
]);
check("POS search hides resolver action in final surface", !read("components/pos/pos-product-search.tsx").includes("Resolver código"), "components/pos/pos-product-search.tsx");
hasAll("components/pos/pos-product-list.tsx", [
  "onAdd(product)",
  "disabled={disabled}",
  "Agregar",
  "ProductGrid"
]);
hasAll("components/pos/pos-ticket-panel.tsx", [
  "Cobrar",
  "QuantityStepper",
  "onIncrement",
  "onDecrement",
  "onRemove",
  "onCheckout",
  "onHold",
  "onRestoreHeldCart",
  "onDiscardHeldCart",
  "Cancelar"
]);

const checkoutScreen = hasAll("components/checkout/checkout-screen.tsx", [
  "role=\"dialog\"",
  "completeCartSale",
  "getOrCreatePaymentRequestId",
  "clearCartStorage()",
  "clearPaymentRequestRecord",
  "paymentTenders",
  "Volver al ticket",
  "Cancelar cobro",
  "inert"
]);
check("checkout persiste resultado antes de limpiar el carrito", checkoutScreen.indexOf("setLastSale(sale)") < checkoutScreen.indexOf("clearCartStorage()"), "components/checkout/checkout-screen.tsx");

const cartState = hasAll("src/lib/pos/cart-state.ts", [
  "POS_CART_STORAGE_KEY",
  "writeCartToStorage",
  "clearCartStorage",
  "emitCartUpdated",
  "prisma:tablet-cart-updated"
]);
check("cart writes and clears broadcast cart refresh", countNeedle(cartState, "emitCartUpdated(") >= 3, "src/lib/pos/cart-state.ts");

hasAll("components/shift/shift-cash-closure-screen.tsx", [
  "loadCurrentShift",
  "/api/pos/shift/current",
  "/api/pos/shift/open",
  "/api/pos/shift/close",
  "Abrir turno",
  "Cerrar turno",
  "Actualizar"
]);
hasAll("app/shift/page.tsx", ["ShiftWorkspace", "getTabletRuntimeSnapshot", "force-dynamic"]);

const sync = hasAll("components/sync/pending-offline-sync-panel-screen.tsx", [
  "dispatchNow",
  "retryFailed",
  "loadPanelOnly",
  "/api/pos/sync/dispatch",
  "/api/pos/sync/retry",
  "Enviar pendientes",
  "Actualizar estado",
  "Reintentar fallidos"
]);
check("sync recarga estado después de dispatch/retry", countNeedle(sync, "loadPanelOnly()") >= 4, "components/sync/pending-offline-sync-panel-screen.tsx");
const catalogPull = hasAll("components/sync/catalog-pull-panel.tsx", [
  "/api/pos/sync/pull",
  "method: \"POST\"",
  "setStatus(response.data)",
  "Actualizar datos",
  "Primera carga",
  "Reparar datos",
  "Actualizar"
]);
check("catalog pull refreshes status after mutation", countNeedle(catalogPull, "setStatus(response.data)") >= 3, "components/sync/catalog-pull-panel.tsx");

hasAll("components/offline/offline-export-audit-screen.tsx", [
  "OfflineResilienceWorkspace",
  "/api/pos/offline/audit?limit=40",
  "Actualizar",
  "Ventas CSV",
  "Pendientes JSON",
  "Movimientos CSV"
]);
hasAll("app/offline/page.tsx", ["OfflineResilienceWorkspace"]);

const catalogStock = hasAll("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx", [
  "loadProducts",
  "resolveCode",
  "addToSale",
  "addSellingAssistProductToCart",
  "prisma:tablet-cart-updated",
  "Buscar",
  "Escanear",
  "StockExportMenu",
  "Limpiar",
  "Agregar a venta"
]);
check("catalog/stock listens for cart and catalog refresh events", catalogStock.includes("prisma:tablet-catalog-updated") && catalogStock.includes("handleCart"), "components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx");
hasAll("app/catalog/page.tsx", ["ProductCatalogWorkspace", "force-dynamic"]);
hasAll("app/stock/page.tsx", ["InventoryWorkspace", 'currentPath="/stock"']);
check("stock route no longer mounts default export overlay", !read("app/stock/page.tsx").includes("ContextualExportBand"), "app/stock/page.tsx");
hasAll("app/existencias/page.tsx", ["InventoryWorkspace", 'currentPath="/existencias"']);

hasAll("components/sales/sales-today-screen.tsx", [
  "/api/pos/sales/today",
  "filterTickets",
  "ContextualExportActions",
  "Volver a vender"
]);
hasAll("components/sales/sales-history-screen.tsx", [
  "/api/pos/sales/history",
  "reloadToken",
  "Aplicar rango",
  "filterTickets"
]);

const posCss = hasAll("components/pos/pos.module.css", [
  "@media (max-width: 980px)",
  "grid-template-columns",
  "prefers-reduced-transparency"
]);
const checkoutCss = hasAll("components/checkout/checkout.module.css", ["@media (max-width: 1179px)", "prefers-reduced-motion", "grid-template-columns"]);
const stockCss = hasAll("components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css", [
  "@media (max-width: 980px)",
  "@media (max-width: 680px)",
  "grid-template-columns"
]);
const shellCss = hasAll("components/tablet-shell/prisma-tablet-shell.module.css", [
  "@media",
  "grid-template-columns",
  ".bottomDockInner",
  ".compactSellingShell",
  "min-height: 52px",
  "prefers-reduced-transparency"
]);
check("POS CSS keeps responsive fallback", posCss.includes("grid-template-columns: 1fr"), "components/pos/pos.module.css");
check("checkout CSS mantiene fallback gobernado", checkoutCss.includes("max-width: 1179px"), "components/checkout/checkout.module.css");
check("stock CSS keeps single-column fallback", stockCss.includes("grid-template-columns: 1fr"), "components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css");
check("shell CSS keeps adaptive shell", shellCss.includes("minmax"), "components/tablet-shell/prisma-tablet-shell.module.css");
check("shell CSS keeps viewport-height baseline", /min-height:\s*100(?:dvh|svh|vh)/.test(shellCss), "components/tablet-shell/prisma-tablet-shell.module.css");
check("shell conserva targets táctiles", /min-height:\s*(?:4[4-9]|5\d)px/.test(shellCss), "components/tablet-shell/prisma-tablet-shell.module.css");

const salesCss = hasAll("components/sales/sales.module.css", [
  "@media (max-width: 720px)",
  "grid-template-columns"
]);
const shiftCss = hasAll("components/shift/shift-cash-closure.module.css", [
  "grid-template-columns",
  "@media"
]);
const syncCss = hasAll("components/sync/pending-offline-sync-panel.module.css", [
  "repeat(auto-fit, minmax(160px, 1fr))",
  "grid-template-columns"
]);
const offlineCss = hasAll("components/offline/offline-export-audit.module.css", [
  "@media (max-width: 760px)",
  "grid-template-columns"
]);
check("sales keeps responsive detail fallback", salesCss.includes("grid-template-columns: 1fr"), "components/sales/sales.module.css");
check("shift keeps responsive workspace fallback", shiftCss.includes("grid-template-columns: 1fr"), "components/shift/shift-cash-closure.module.css");
check("sync keeps intrinsic responsive grids", syncCss.includes("auto-fit"), "components/sync/pending-offline-sync-panel.module.css");
check("offline keeps responsive export fallback", offlineCss.includes("grid-template-columns: 1fr"), "components/offline/offline-export-audit.module.css");

if (failures.length) {
  console.error("PRISMA_TABLET_FUNCTIONAL_VISUAL_CLEANUP_0605 FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_TABLET_FUNCTIONAL_VISUAL_CLEANUP_0605 PASS (canonical owners reconciled)");
