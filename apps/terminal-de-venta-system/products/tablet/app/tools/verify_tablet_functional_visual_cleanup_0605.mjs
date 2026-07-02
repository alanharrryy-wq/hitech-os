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

const posPage = hasAll("app/pos/page.tsx", ["PosScreen", "force-dynamic"]);
const checkoutPage = hasAll("app/checkout/page.tsx", ["PosScreen", "force-dynamic"]);
check("/checkout remains unified with POS flow", checkoutPage.includes("<PosScreen"), "app/checkout/page.tsx");

const posScreen = hasAll("components/pos/pos-screen.tsx", [
  "PosProductSearch",
  "PosProductList",
  "PosTicketPanel",
  "PosCobroSurface",
  "completeCartSale",
  "await loadProducts(query)",
  "setLastReceipt(receipt)",
  "setCart([])",
  "clearCartStorage()",
  "onIncrement",
  "onDecrement",
  "onRemove",
  "onClear",
  "onCheckout"
]);
check("POS keeps governed light preset", posScreen.includes('visualPreset="PRISMA_LIGHT_OPERATIONAL_POS"'), "components/pos/pos-screen.tsx");
check("POS page participates in this gate", Boolean(posPage), "app/pos/page.tsx");

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
  "Guardar ticket",
  "Opciones de ticket",
  "Cancelar venta"
]);
hasAll("components/pos/pos-cobro-surface.tsx", [
  "role=\"dialog\"",
  "onPaymentTenderChange",
  "onConfirm",
  "Completar pago",
  "Volver al ticket",
  "Cancelar cobro",
  "data-prisma-checkout-finalize"
]);

const cartState = hasAll("src/lib/pos/cart-state.ts", [
  "POS_CART_STORAGE_KEY",
  "writeCartToStorage",
  "clearCartStorage",
  "emitCartUpdated",
  "prisma:tablet-cart-updated"
]);
check("cart writes and clears broadcast cart refresh", countNeedle(cartState, "emitCartUpdated(") >= 3, "src/lib/pos/cart-state.ts");

const shift = hasAll("components/shift/shift-cash-closure-screen.tsx", [
  "loadCurrentShift",
  "/api/pos/shift/current",
  "/api/pos/shift/open",
  "/api/pos/shift/close",
  "setShift(response.data.shift)",
  "Abrir turno",
  "Cerrar turno",
  "Actualizar"
]);
check("shift open and close both update visible state", countNeedle(shift, "setShift(response.data.shift)") >= 2, "components/shift/shift-cash-closure-screen.tsx");
hasAll("app/shift/page.tsx", ["ShiftCashClosureScreen", "force-dynamic"]);

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
check("sync reloads panel after dispatch/retry attempts", countNeedle(sync, "await loadPanelOnly()") >= 4, "components/sync/pending-offline-sync-panel-screen.tsx");
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
  "load()",
  "/api/pos/offline/audit?limit=40",
  "Actualizar",
  "Ventas CSV",
  "Pendientes JSON",
  "Movimientos CSV"
]);
hasAll("app/offline/page.tsx", ["OfflineExportAuditScreen"]);

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
hasAll("app/catalog/page.tsx", ["CatalogScreen", "force-dynamic"]);
hasAll("app/stock/page.tsx", ["CatalogStockSellingAssistScreen", "mode=\"stock\""]);
check("stock route no longer mounts default export overlay", !read("app/stock/page.tsx").includes("ContextualExportBand"), "app/stock/page.tsx");
hasAll("app/existencias/page.tsx", ["CatalogStockSellingAssistScreen", "mode=\"stock\""]);

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
  "@media (max-height: 920px)",
  "grid-template-columns",
  "100dvh",
  "PRISMA_TABLET_ADAPTIVE_VISUAL_CLEANUP_0605::POS_START",
  ".paymentPanelCard"
]);
const checkoutCss = hasAll("components/checkout/checkout.module.css", ["@media (max-width: 980px)", "@media (max-width: 640px)", "grid-template-columns"]);
const stockCss = hasAll("components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css", [
  "@media (max-width: 1180px)",
  "@media (max-width: 760px)",
  "grid-template-columns",
  "PRISMA_TABLET_ADAPTIVE_VISUAL_CLEANUP_0605::CATALOG_STOCK_START"
]);
const shellCss = hasAll("components/tablet-shell/prisma-tablet-shell.module.css", [
  "@media",
  "grid-template-columns",
  ".bottomDockInner",
  ".compactSellingShell",
  "min-height: 52px"
]);
check("POS CSS keeps responsive fallback", posCss.includes("grid-template-columns: 1fr"), "components/pos/pos.module.css");
check("checkout CSS keeps single-column fallback", checkoutCss.includes("grid-template-columns: 1fr"), "components/checkout/checkout.module.css");
check("stock CSS keeps single-column fallback", stockCss.includes("grid-template-columns: 1fr"), "components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css");
check("shell CSS keeps adaptive shell", shellCss.includes("minmax"), "components/tablet-shell/prisma-tablet-shell.module.css");
check("shell CSS keeps viewport-height baseline", /min-height:\s*100(?:dvh|svh|vh)/.test(shellCss), "components/tablet-shell/prisma-tablet-shell.module.css");
check("POS shell hides oversized title header", shellCss.includes(".compactSellingShell .main") && shellCss.includes("grid-template-rows: minmax(0, 1fr)"), "components/tablet-shell/prisma-tablet-shell.module.css");
check("POS shell removes fixed outer frame", shellCss.includes("inset: 0") && shellCss.includes("border: 0") && shellCss.includes("box-shadow: none"), "components/tablet-shell/prisma-tablet-shell.module.css");
check("POS products use final compact auto-fit grid", posCss.includes("repeat(auto-fit, minmax(156px, 1fr))"), "components/pos/pos.module.css");
check("checkout payment card keeps landscape split", posCss.includes("grid-template-columns: minmax(260px, 0.88fr) minmax(320px, 1.12fr)"), "components/pos/pos.module.css");
check("catalog/stock rows keep adaptive add action fallback", stockCss.includes(".rowAddButton") && stockCss.includes("grid-column: 1 / -1"), "components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css");

const salesCss = hasAll("components/sales/sales.module.css", [
  "PRISMA_TABLET_ADAPTIVE_VISUAL_CLEANUP_0605::SALES_START",
  "repeat(auto-fit, minmax(150px, 1fr))",
  "@media (max-width: 820px)"
]);
const shiftCss = hasAll("components/shift/shift-cash-closure.module.css", [
  "grid-template-columns",
  "@media"
]);
const syncCss = hasAll("components/sync/pending-offline-sync-panel.module.css", [
  "PRISMA_TABLET_ADAPTIVE_VISUAL_CLEANUP_0605::SYNC_START",
  "repeat(auto-fit, minmax(142px, 1fr))",
  "repeat(auto-fit, minmax(118px, 1fr))"
]);
const offlineCss = hasAll("components/offline/offline-export-audit.module.css", [
  "PRISMA_TABLET_ADAPTIVE_VISUAL_CLEANUP_0605::OFFLINE_START",
  "repeat(auto-fit, minmax(142px, 1fr))",
  "repeat(auto-fit, minmax(136px, 1fr))"
]);
check("sales keeps responsive detail fallback", salesCss.includes("grid-template-columns: 1fr"), "components/sales/sales.module.css");
check("shift keeps responsive workspace fallback", shiftCss.includes("grid-template-columns: 1fr"), "components/shift/shift-cash-closure.module.css");
check("sync keeps responsive item fallback", syncCss.includes("grid-template-columns: 1fr"), "components/sync/pending-offline-sync-panel.module.css");
check("offline keeps responsive export fallback", offlineCss.includes("grid-template-columns: 1fr"), "components/offline/offline-export-audit.module.css");

if (failures.length) {
  console.error("PRISMA_TABLET_FUNCTIONAL_VISUAL_CLEANUP_0605 FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_TABLET_FUNCTIONAL_VISUAL_CLEANUP_0605 PASS");
