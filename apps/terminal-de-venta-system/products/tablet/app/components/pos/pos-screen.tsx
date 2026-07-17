"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { motion } from "motion/react";
import type { CartLine, PosProduct, UiState } from "@/lib/pos/cart-state";
import { cartTotalCents, cartTotalQty, clearCartStorage, formatMoney, readCartFromStorage, requestJson, writeCartToStorage } from "@/lib/pos/cart-state";
import { addProductToCart, clearCart, decrementCartLine, incrementCartLine, removeCartLine, validateCartForCheckout } from "@/lib/pos/cart-engine";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { checkoutStateCopy, checkoutStateTone, isCheckoutBusy } from "@/lib/pos/payment-contract";
import { clearPaymentRequestRecord } from "@/lib/pos/payment-idempotency";
import type { HeldCart } from "@/lib/pos/held-carts";
import { addHeldCart, readHeldCartsFromStorage, removeHeldCart, writeHeldCartsToStorage } from "@/lib/pos/held-carts";
import { PosProductSearch } from "./pos-product-search";
import { PosProductList } from "./pos-product-list";
import { PosTicketPanel } from "./pos-ticket-panel";
import { PosLiveBinding } from "./pos-live-binding";
import { PosCommandDock, PosProductCanvas, PosTerminalBody, PosTerminalHeader, PosTerminalSurface, PosTicketRail } from "./terminal-v2";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import styles from "./pos.module.css";


const FEATURED_CATEGORY = "Más vendidos";

type ShowcaseFamilyRule = {
  key: string;
  any: string[];
  categoryHint?: string;
};

const SHOWCASE_FAMILIES: ShowcaseFamilyRule[] = [
  { key: "aceite", any: ["aceite", "capullo", "patrona"], categoryHint: "Abarrotes" },
  { key: "agua", any: ["agua", "bonafont", "ciel", "cristal", "mineral"], categoryHint: "Bebidas" },
  { key: "leche", any: ["leche", "lala", "deslactosada", "descremada"], categoryHint: "Lácteos" },
  { key: "pan", any: ["pan", "bimbo", "bolillo"], categoryHint: "Panadería" },
  { key: "huevos", any: ["huevo", "huevos"], categoryHint: "Abarrotes" },
  { key: "botana", any: ["papas", "sabritas", "doritos", "cheetos", "takis", "ruffles", "tostitos"], categoryHint: "Botanas" },
  { key: "dulce", any: ["galletas", "clorets", "halls", "chocolate", "mazapan", "mazapán", "duvalin", "kinder", "m&m"], categoryHint: "Dulces" },
  { key: "atun", any: ["atun", "atún", "dolores"], categoryHint: "Abarrotes" },
  { key: "arroz", any: ["arroz", "verde valle"], categoryHint: "Abarrotes" },
  { key: "cafe", any: ["cafe", "café", "nescafe", "nescafé"], categoryHint: "Abarrotes" },
  { key: "detergente", any: ["detergente", "ace detergente", "limpiador", "lavatrastes", "blanqueador"], categoryHint: "Limpieza" },
  { key: "higiene", any: ["jabon", "jabón", "shampoo", "pasta dental", "desodorante", "papel higienico", "papel higiénico"], categoryHint: "Higiene" },
  { key: "queso", any: ["queso", "oaxaca", "manchego", "panela", "cheddar"], categoryHint: "Lácteos" },
  { key: "cereal", any: ["cereal", "zucaritas", "avena", "quaker"], categoryHint: "Cereales" },
  { key: "pasta", any: ["pasta", "espagueti", "spaghetti", "harina"], categoryHint: "Abarrotes" }
];

function normalizeShowcaseText(value: string | null | undefined) {
  return (value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function includesShowcaseNeedle(text: string, needles: string[]) {
  return needles.some((needle) => text.includes(normalizeShowcaseText(needle)));
}

function showcaseFamily(product: PosProduct) {
  const text = normalizeShowcaseText(`${product.name} ${product.category ?? ""} ${product.sku ?? ""}`);
  const direct = SHOWCASE_FAMILIES.find((family) => includesShowcaseNeedle(text, family.any));
  if (direct) return direct.key;

  const category = normalizeShowcaseText(product.category);
  const byCategory = SHOWCASE_FAMILIES.find((family) => family.categoryHint && normalizeShowcaseText(family.categoryHint) === category);
  return byCategory?.key ?? `zz-${category || "general"}`;
}

function stockPriority(product: PosProduct) {
  if (!product.isActive) return 100_000;
  if (product.stockOnHand <= 0) return 90_000;
  return Math.max(0, 2_000 - product.stockOnHand);
}

function compareShowcaseProducts(a: PosProduct, b: PosProduct) {
  const stockDelta = stockPriority(a) - stockPriority(b);
  if (stockDelta !== 0) return stockDelta;
  return a.name.localeCompare(b.name, "es-MX");
}

function buildFeaturedProducts(products: PosProduct[]) {
  const sorted = [...products].sort(compareShowcaseProducts);
  const firstByFamily = new Map<string, PosProduct>();
  const overflow: PosProduct[] = [];

  for (const product of sorted) {
    const family = showcaseFamily(product);
    if (!firstByFamily.has(family)) {
      firstByFamily.set(family, product);
      continue;
    }
    overflow.push(product);
  }

  const familyOrder = SHOWCASE_FAMILIES.map((family) => family.key);
  const featured = familyOrder
    .map((family) => firstByFamily.get(family))
    .filter((product): product is PosProduct => Boolean(product));

  const extraFamilies = [...firstByFamily.entries()]
    .filter(([family]) => !familyOrder.includes(family))
    .map(([, product]) => product)
    .sort(compareShowcaseProducts);

  return [...featured, ...extraFamilies, ...overflow];
}

function looksLikeScannedCode(value: string) {
  const clean = value.trim();
  return /^\d{6,14}$/.test(clean) || /^[A-Z0-9][A-Z0-9_-]{5,}$/i.test(clean);
}

export function SellingWorkspace({
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT,
  checkoutBackdrop = false
}: {
  runtimeSnapshot?: TabletRuntimeSnapshot;
  checkoutBackdrop?: boolean;
}) {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [productState, setProductState] = useState<UiState>("idle");
  const [productError, setProductError] = useState<unknown>(null);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [cartHydrated, setCartHydrated] = useState(false);
  const [heldCarts, setHeldCarts] = useState<HeldCart[]>([]);
  const [selectedCategory, setSelectedCategory] = useState(FEATURED_CATEGORY);
  const [checkoutState, setCheckoutState] = useState<CheckoutState>("idle");
  const [checkoutError, setCheckoutError] = useState<unknown>(null);

  const categories = useMemo(
    () => [FEATURED_CATEGORY, ...Array.from(new Set(products.map((product) => product.category?.trim()).filter(Boolean) as string[])).sort((a, b) => a.localeCompare(b, "es-MX"))],
    [products]
  );
  const featuredProducts = useMemo(() => buildFeaturedProducts(products), [products]);
  const visibleProducts = selectedCategory === FEATURED_CATEGORY ? featuredProducts : products.filter((product) => (product.category?.trim() || "General") === selectedCategory);
  const activeProductCount = products.filter((product) => product.isActive).length;
  const checkoutBusy = isCheckoutBusy(checkoutState);
  const checkoutReady = validateCartForCheckout(cart);
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(runtimeSnapshot), [runtimeSnapshot]);
  const cartQty = cartTotalQty(cart);
  const cartTotal = cartTotalCents(cart);
  const newProductHref = useMemo(() => {
    const scanned = query.trim();
    if (!scanned) return "/catalog?new=1";
    return `/catalog?new=1&sku=${encodeURIComponent(scanned)}`;
  }, [query]);

  function setHeldCartShelf(next: HeldCart[]) {
    setHeldCarts(next);
    writeHeldCartsToStorage(next);
  }

  async function loadProducts(nextQuery = query) {
    if (!gate.canOperatePos) {
      setProductState("idle");
      return;
    }
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

  async function resolveCode(nextQuery = query, options: { fallbackSearch?: boolean } = {}) {
    if (!gate.canAddProduct) {
      setCheckoutError(gate.detail);
      setCheckoutState("error");
      return;
    }
    const cleanQuery = nextQuery.trim();
    if (!cleanQuery) return;
    setProductError(null);
    try {
      const response = await requestJson<{ product: PosProduct }>(`/api/pos/products/resolve?code=${encodeURIComponent(cleanQuery)}`);
      setProducts([response.data.product]);
      setProductState("ready");
      addProduct(response.data.product);
      setQuery("");
    } catch (error) {
      if (options.fallbackSearch) {
        await loadProducts(cleanQuery);
        return;
      }
      setProductError(error);
      setProductState("error");
    }
  }

  async function runPrimaryLookup(nextQuery = query) {
    const cleanQuery = nextQuery.trim();
    if (looksLikeScannedCode(cleanQuery)) {
      await resolveCode(cleanQuery, { fallbackSearch: true });
      return;
    }
    await loadProducts(cleanQuery);
  }

  function addProduct(product: PosProduct) {
    if (!gate.canAddProduct) {
      setCheckoutError(gate.detail);
      setCheckoutState("error");
      return;
    }
    setCheckoutState("idle");
    setCheckoutError(null);
    const result = addProductToCart(cart, product);
    if (result.warning) {
      setCheckoutError(result.warning);
      setCheckoutState("error");
    }
    setCart(result.lines);
  }

  function resetCheckoutState() {
    setCheckoutState("idle");
    setCheckoutError(null);
    clearPaymentRequestRecord();
  }

  function clearTicket() {
    resetCheckoutState();
    setCart((current) => clearCart(current).lines);
  }

  function holdActiveTicket() {
    if (!cart.length) {
      setCheckoutError("No hay ticket activo para guardar.");
      setCheckoutState("error");
      return;
    }
    const result = addHeldCart(heldCarts, cart);
    if (result.warning || !result.heldCart) {
      setCheckoutError(result.warning ?? "No pudimos guardar el ticket.");
      setCheckoutState("error");
      return;
    }
    setHeldCartShelf(result.heldCarts);
    resetCheckoutState();
    setCart([]);
    clearCartStorage();
  }

  function restoreHeldTicket(heldCartId: string) {
    const heldCart = heldCarts.find((item) => item.id === heldCartId);
    if (!heldCart) {
      setCheckoutError("Ese ticket guardado ya no existe.");
      setCheckoutState("error");
      return;
    }
    if (cart.length) {
      setCheckoutError("Guarda o limpia el ticket actual antes de recuperar otro.");
      setCheckoutState("error");
      return;
    }
    resetCheckoutState();
    setCart(heldCart.lines);
    setHeldCartShelf(removeHeldCart(heldCarts, heldCartId));
  }

  function discardHeldTicket(heldCartId: string) {
    setHeldCartShelf(removeHeldCart(heldCarts, heldCartId));
  }

  function openCheckout() {
    if (!gate.canCheckout) {
      setCheckoutError(gate.detail);
      setCheckoutState("error");
      return;
    }
    const ready = validateCartForCheckout(cart);
    if (!ready.ready) {
      setCheckoutError(ready.reason);
      setCheckoutState("error");
      return;
    }
    setCheckoutError(null);
    setCheckoutState("review");
    writeCartToStorage(cart);
    window.sessionStorage.setItem("prisma.tablet.pos.checkoutReturnFocus.v1", "1");
    window.location.assign("/checkout");
  }

  useEffect(() => {
    setCart(readCartFromStorage());
    setHeldCarts(readHeldCartsFromStorage());
    setCartHydrated(true);
    if (gate.canOperatePos) void loadProducts("");
  }, [gate.canOperatePos]);

  useEffect(() => {
    if (!cartHydrated) return;
    writeCartToStorage(cart);
  }, [cart, cartHydrated]);

  useEffect(() => {
    if (checkoutBackdrop || !cart.length || typeof window === "undefined") return;
    const key = "prisma.tablet.pos.checkoutReturnFocus.v1";
    if (window.sessionStorage.getItem(key) !== "1") return;
    window.sessionStorage.removeItem(key);
    const frame = window.requestAnimationFrame(() => {
      document.querySelector<HTMLElement>('[data-prisma-component="CheckoutButton"]')?.focus();
    });
    return () => window.cancelAnimationFrame(frame);
  }, [cart.length, checkoutBackdrop]);

  useEffect(() => {
    if (!gate.canOperatePos) return;
    const cleanQuery = query.trim();
    if (cleanQuery.length === 1) return;
    const delay = cleanQuery.length >= 2 ? 260 : 120;
    const timer = window.setTimeout(() => {
      void loadProducts(cleanQuery);
    }, delay);
    return () => window.clearTimeout(timer);
  }, [query, gate.canOperatePos]);

  const copy = checkoutStateCopy(checkoutState);

  if (!gate.canOperatePos) {
    return (
      <PrismaTabletShellUnified
        currentPath="/pos"
        title={gate.title}
        subtitle={gate.detail}
        status={<TabletShellStatusPill tone={gate.tone}>{gate.actionLabel}</TabletShellStatusPill>}
        runtimeSnapshot={runtimeSnapshot}
        visualSurface="tablet-pos-nocturne"
        visualPreset="PRISMA_NOCTURNE_REFERENCE_1607"
        showBottomDock={!checkoutBackdrop}
      >
        <PosTerminalSurface
          cartState="blocked"
          paymentOpen={false}
          visualState="blocked"
        >
          <section
            className={`${styles.statePanel} ${styles.posGateDeck}`}
            data-prisma-operational-gate="closed-cash"
            data-prisma-state="blocked"
            data-prisma-panel="tablet.pos.closed-gate"
            data-prisma-visual-unit="tablet.pos.turn-opening-card"
            data-prisma-editable-slot="state-panel.layout,state-panel.spacing,state-panel.surface,state-panel.cta"
            role="status"
            data-surface="tablet"
            data-screen="pos"
            data-zone="checkout"
            data-panel="pos-screen"
            data-target="pos-screen-price-381"
            data-kind="price"
            data-role="financial-control"
          >
            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-div-1" data-kind="panel" data-role="container" className={styles.posGateHero}>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-2" data-kind="text" data-role="text" className={styles.posGateIcon} aria-hidden="true">
                <PrismaIcon name="terminal" size={30} />
              </span>
              <span className={styles.posGateEyebrow}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-screen"
                data-target="pos-screen-table-394"
                data-kind="table"
                data-role="data-display"
              >Tablet vende sola</span>
              <strong className={styles.posGateTitle}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-screen"
                data-target="pos-screen-text-395"
                data-kind="text"
                data-role="copy"
              >Caja cerrada</strong>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-3" data-kind="text" data-role="text" className={styles.posGateDetail}>{gate.detail}</span>
            </div>

            <div className={styles.posGateMetaGrid} aria-label="Resumen operativo de caja"
              data-surface="tablet"
              data-screen="pos"
              data-zone="pos"
              data-panel="pos-screen"
              data-target="pos-screen-resumen-operativo-de-caja-399"
              data-kind="text"
              data-role="copy"
            >
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-4" data-kind="text" data-role="text" className={styles.posGateMeta}>
                <small>Sucursal</small>
                <strong
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-screen"
                  data-target="pos-screen-element-402"
                  data-kind="element"
                  data-role="revenue-core"
                >{runtimeSnapshot.identity.storeName}</strong>
              </span>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-5" data-kind="text" data-role="text" className={styles.posGateMeta}>
                <small>Terminal</small>
                <strong
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-screen"
                  data-target="pos-screen-element-406"
                  data-kind="element"
                  data-role="revenue-core"
                >{runtimeSnapshot.identity.terminalName}</strong>
              </span>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-6" data-kind="text" data-role="text" className={styles.posGateMeta}>
                <small>Operador</small>
                <strong
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-screen"
                  data-target="pos-screen-element-410"
                  data-kind="element"
                  data-role="revenue-core"
                >{runtimeSnapshot.identity.operatorName}</strong>
              </span>
            </div>

            <div className={styles.posGateActions}
              data-surface="tablet"
              data-screen="pos"
              data-zone="pos"
              data-panel="pos-screen"
              data-target="pos-screen-button-414"
              data-kind="button"
              data-role="action"
            >
              <a className={styles.posPremiumBlockedGateAction} href={gate.actionHref}
                data-surface="tablet"
                data-screen="pos"
                data-zone="pos"
                data-panel="pos-screen"
                data-target="pos-screen-button-415"
                data-kind="button"
                data-role="action"
              >
                <PrismaIcon name="terminal" size={18} />
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-7" data-kind="text" data-role="text">{gate.actionLabel}</span>
              </a>
              <small>Abre el turno para activar venta, catálogo y cobro.</small>
            </div>
          </section>
        </PosTerminalSurface>
      </PrismaTabletShellUnified>
    );
  }

  return (
    <PrismaTabletShellUnified
      currentPath="/pos"
      title="Vender"
      kicker={runtimeSnapshot.identity.storeName}
      subtitle={`${runtimeSnapshot.identity.terminalName} · ${runtimeSnapshot.identity.operatorName}`}
      status={<TabletShellStatusPill tone={checkoutStateTone(checkoutState)}>{copy.label}</TabletShellStatusPill>}
      visualSurface="tablet-pos-nocturne"
      runtimeSnapshot={runtimeSnapshot}
      visualPreset="PRISMA_NOCTURNE_REFERENCE_1607"
      showBottomDock={!checkoutBackdrop}
    >
      <PosTerminalSurface
        cartState={cart.length ? "active" : "empty"}
        paymentOpen={false}
        visualState={checkoutState === "error" ? "error" : checkoutBusy ? "checkout-busy" : "ready"}
      >
        <PosLiveBinding />
        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="pos_screen" data-target="pos-screen-span-8" data-kind="text" data-role="text" className={styles.posPremiumSceneGlow} aria-hidden="true" />
        <span hidden data-prisma-golden-flow="touch-only-actions-04h" data-prisma-touch-only-actions="04H"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-screen"
          data-target="pos-screen-button-446"
          data-kind="button"
          data-role="action"
        />
        <PosTerminalHeader
          activeCount={activeProductCount}
          cartQty={cartQty}
          cartTotal={formatMoney(cartTotal)}
          statusLabel={copy.label}
          storeName={runtimeSnapshot.identity.storeName}
          terminalName={runtimeSnapshot.identity.terminalName}
        />
        <PosTerminalBody>
          <PosProductCanvas>
            <motion.section
              className={styles.posPremiumCatalogArea}
              data-prisma-role="operational-summary"
              data-prisma-priority="primary"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            >
              <PosProductSearch
                query={query}
                setQuery={setQuery}
                loading={productState === "loading"}
                error={productError}
                resultCount={visibleProducts.length}
                state={productState}
                onSearch={() => void runPrimaryLookup(query)}
                onClear={() => {
                  setQuery("");
                  void loadProducts("");
                }}
              />
              <PosCommandDock>
                <nav
                  className={styles.posPremiumCategoryRail}
                  data-prisma-panel="tablet.pos.category-rail"
                  data-prisma-surface="tablet"
                  data-prisma-route="/pos"
                  data-prisma-zone="tablet-pos-category-chips"
                  data-prisma-role="secondary-action"
                  data-prisma-priority="support"
                  data-surface="tablet"
                  data-screen="pos"
                  data-zone="pos"
                  data-panel="pos-screen"
                  data-target="pos-screen-button-479"
                  data-kind="button"
                  data-role="action"
                >
                  {categories.map((category, index) => (
                    <motion.button
                      key={category}
                      className={category === selectedCategory ? styles.posPremiumCategoryButtonActive : styles.posPremiumCategoryButton}
                      type="button"
                      onClick={() => setSelectedCategory(category)}
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      whileTap={{ scale: 0.98 }}
                      whileHover={{ y: -1 }}
                      transition={{ duration: 0.16, delay: Math.min(index * 0.018, 0.16), ease: [0.22, 1, 0.36, 1] }}
                      data-prisma-component="CategoryButton"
                      data-active={category === selectedCategory ? "true" : "false"}
                      data-prisma-role="secondary-action"
                      data-prisma-priority={category === selectedCategory ? "primary" : "support"}
                      data-prisma-state={category === selectedCategory ? "selected" : undefined}
                      data-prisma-motion="press-feedback"
                    >
                      <strong
                        data-surface="tablet"
                        data-screen="pos"
                        data-zone="pos"
                        data-panel="pos-screen"
                        data-target="pos-screen-element-506"
                        data-kind="element"
                        data-role="revenue-core"
                      >{category}</strong>
                    </motion.button>
                  ))}
                </nav>
              </PosCommandDock>
              <PosProductList
                products={visibleProducts}
                state={productState}
                error={productError}
                query={query}
                newProductHref={newProductHref}
                canAddProduct={gate.canAddProduct}
                blockedReason={gate.detail}
                onAdd={addProduct}
                onSearchAgain={() => void runPrimaryLookup(query)}
                onCancelSearch={() => {
                  setQuery("");
                  void loadProducts("");
                }}
              />
            </motion.section>
          </PosProductCanvas>

          <PosTicketRail>
            <PosTicketPanel
              lines={cart}
              heldCarts={heldCarts}
              checkoutBusy={checkoutBusy}
              checkoutError={checkoutError}
              checkoutReason={checkoutReady.reason}
              canCheckout={gate.canCheckout}
              checkoutBlockedReason={gate.detail}
              onIncrement={(productId) => setCart((current) => incrementCartLine(current, productId).lines)}
              onDecrement={(productId) => setCart((current) => decrementCartLine(current, productId).lines)}
              onRemove={(productId) => setCart((current) => removeCartLine(current, productId).lines)}
              onClear={clearTicket}
              onHold={holdActiveTicket}
              onRestoreHeldCart={restoreHeldTicket}
              onDiscardHeldCart={discardHeldTicket}
              onCheckout={() => void openCheckout()}
            />
          </PosTicketRail>
        </PosTerminalBody>
      </PosTerminalSurface>

    </PrismaTabletShellUnified>
  );
}

export const PosScreen = SellingWorkspace;
