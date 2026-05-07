"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import type { CartLine, CompletedSaleReceipt, PosProduct, UiState } from "@/lib/pos/cart-state";
import { clearCartStorage, readCartFromStorage, requestJson, writeCartToStorage } from "@/lib/pos/cart-state";
import { addProductToCart, clearCart, decrementCartLine, incrementCartLine, removeCartLine, validateCartForCheckout } from "@/lib/pos/cart-engine";
import type { PaymentMethod } from "@/lib/pos/payment-state";
import { completeCartSale } from "@/lib/pos/payment-flow";
import type { CheckoutState } from "@/lib/pos/payment-contract";
import { checkoutStateCopy, checkoutStateTone, isCheckoutBusy } from "@/lib/pos/payment-contract";
import { clearPaymentRequestRecord, getOrCreatePaymentRequestId } from "@/lib/pos/payment-idempotency";
import type { HeldCart } from "@/lib/pos/held-carts";
import { addHeldCart, readHeldCartsFromStorage, removeHeldCart, writeHeldCartsToStorage } from "@/lib/pos/held-carts";
import { PosProductSearch } from "./pos-product-search";
import { PosProductList } from "./pos-product-list";
import { PosTicketPanel } from "./pos-ticket-panel";
import { PosPaymentPanel } from "./pos-payment-panel";
import { PosSaleSuccess } from "./pos-sale-success";
import { PosLiveBinding } from "./pos-live-binding";
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

export function PosScreen() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [productState, setProductState] = useState<UiState>("idle");
  const [productError, setProductError] = useState<unknown>(null);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [heldCarts, setHeldCarts] = useState<HeldCart[]>([]);
  const [selectedCategory, setSelectedCategory] = useState(FEATURED_CATEGORY);
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [cashReceivedCents, setCashReceivedCents] = useState(0);
  const [checkoutState, setCheckoutState] = useState<CheckoutState>("idle");
  const [checkoutError, setCheckoutError] = useState<unknown>(null);
  const [clientRequestId, setClientRequestId] = useState("");
  const [lastReceipt, setLastReceipt] = useState<CompletedSaleReceipt | null>(null);

  const categories = useMemo(
    () => [FEATURED_CATEGORY, ...Array.from(new Set(products.map((product) => product.category?.trim()).filter(Boolean) as string[])).sort((a, b) => a.localeCompare(b, "es-MX"))],
    [products]
  );
  const featuredProducts = useMemo(() => buildFeaturedProducts(products), [products]);
  const visibleProducts = selectedCategory === FEATURED_CATEGORY ? featuredProducts : products.filter((product) => (product.category?.trim() || "General") === selectedCategory);
  const activeProductCount = products.filter((product) => product.isActive).length;
  const checkoutBusy = isCheckoutBusy(checkoutState);
  const checkoutReady = validateCartForCheckout(cart);

  function setHeldCartShelf(next: HeldCart[]) {
    setHeldCarts(next);
    writeHeldCartsToStorage(next);
  }

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

  async function resolveCode(nextQuery = query, options: { fallbackSearch?: boolean } = {}) {
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
    setLastReceipt(null);
    setCheckoutState("idle");
    setCheckoutError(null);
    const result = addProductToCart(cart, product);
    if (result.warning) {
      setCheckoutError(result.warning);
      setCheckoutState("error");
    }
    setCart(result.lines);
  }

  function resetPaymentState() {
    setPaymentOpen(false);
    setCheckoutState("idle");
    setCheckoutError(null);
    setCashReceivedCents(0);
    setClientRequestId("");
    clearPaymentRequestRecord();
  }

  function clearTicket() {
    setLastReceipt(null);
    resetPaymentState();
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
    setLastReceipt(null);
    resetPaymentState();
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
    setLastReceipt(null);
    resetPaymentState();
    setCart(heldCart.lines);
    setHeldCartShelf(removeHeldCart(heldCarts, heldCartId));
  }

  function discardHeldTicket(heldCartId: string) {
    setHeldCartShelf(removeHeldCart(heldCarts, heldCartId));
  }

  async function openCheckout() {
    const ready = validateCartForCheckout(cart);
    if (!ready.ready) {
      setCheckoutError(ready.reason);
      setCheckoutState("error");
      return;
    }
    setCheckoutError(null);
    setCheckoutState("review");
    const requestId = clientRequestId || (await getOrCreatePaymentRequestId(cart));
    setClientRequestId(requestId);
    setPaymentOpen(true);
  }

  async function confirmSale() {
    if (checkoutBusy) return;
    const requestId = clientRequestId || (await getOrCreatePaymentRequestId(cart));
    setClientRequestId(requestId);
    setCheckoutState("submitting");
    setCheckoutError(null);
    try {
      const receipt = await completeCartSale({ lines: cart, paymentMethod, cashReceivedCents, clientRequestId: requestId });
      setLastReceipt(receipt);
      setCart([]);
      clearCartStorage();
      clearPaymentRequestRecord();
      setPaymentOpen(false);
      setCashReceivedCents(0);
      setCheckoutState("success");
      await loadProducts(query);
    } catch (error) {
      setCheckoutError(error);
      setCheckoutState("error");
    }
  }

  useEffect(() => {
    setCart(readCartFromStorage());
    setHeldCarts(readHeldCartsFromStorage());
    void loadProducts("");
  }, []);

  useEffect(() => {
    writeCartToStorage(cart);
  }, [cart]);

  const copy = checkoutStateCopy(checkoutState);

  return (
    <PrismaTabletShellUnified
      currentPath="/pos"
      title="Vender"
      subtitle="Busca, escanea, arma el ticket y cobra aquí mismo."
      status={<TabletShellStatusPill tone={checkoutStateTone(checkoutState)}>{copy.label}</TabletShellStatusPill>}
      visualSurface="tablet-pos"
      visualPreset="PRISMA_LIGHT_OPERATIONAL_POS"
    >
      <div
        className={styles.posWorkspace}
        data-prisma-component="PointOfSaleWorkspace"
        data-prisma-vos-note="PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B"
        data-prisma-zone="tablet-pos-root"
        data-prisma-role="operational-summary"
        data-prisma-priority="primary"
        data-prisma-motion="ambient"
        data-prisma-qa="tablet-qa-pos"
        data-prisma-vos="00B"
        data-prisma-vos-stage="00F_00I"
        data-prisma-vsurface="tablet-pos"
        data-prisma-vpreset="POS_TOUCH"
        data-prisma-golden-flow="touch-guided-sidebar-04i"
        data-prisma-light-operational="00Q"
        data-prisma-pos-live="00T"
        data-prisma-layer="surface"
        data-prisma-cart-state={cart.length ? "active" : "empty"}
        data-prisma-visual-state={checkoutState === "error" ? "error" : checkoutBusy ? "checkout-busy" : "ready"}
      >
        <PosLiveBinding />
        <span hidden data-prisma-golden-flow="touch-only-actions-04h" data-prisma-touch-only-actions="04H" />
        <section className={styles.catalogArea} data-prisma-role="operational-summary" data-prisma-priority="primary">
          <PosProductSearch
            query={query}
            setQuery={setQuery}
            loading={productState === "loading"}
            error={productError}
            resultCount={visibleProducts.length}
            activeCount={activeProductCount}
            state={productState}
            onSearch={() => void runPrimaryLookup(query)}
            onResolve={() => void resolveCode(query)}
            onClear={() => {
              setQuery("");
              void loadProducts("");
            }}
          />
          <nav
            className={styles.categoryRail}
            data-prisma-zone="tablet-pos-category-chips"
            data-prisma-role="secondary-action"
            data-prisma-priority="support"
          >
            {categories.map((category) => (
              <button
                key={category}
                className={category === selectedCategory ? styles.categoryButtonActive : styles.categoryButton}
                type="button"
                onClick={() => setSelectedCategory(category)}
                data-prisma-component="CategoryButton"
                data-active={category === selectedCategory ? "true" : "false"}
                data-prisma-role="secondary-action"
                data-prisma-priority={category === selectedCategory ? "primary" : "support"}
                data-prisma-state={category === selectedCategory ? "selected" : undefined}
                data-prisma-motion="press-feedback"
              >
                <span>{category.slice(0, 2).toUpperCase()}</span>
                <strong>{category}</strong>
              </button>
            ))}
          </nav>
          <PosProductList products={visibleProducts} state={productState} error={productError} onAdd={addProduct} />
        </section>

        <PosTicketPanel
          lines={cart}
          heldCarts={heldCarts}
          checkoutBusy={checkoutBusy}
          checkoutError={checkoutError}
          checkoutReason={checkoutReady.reason}
          onIncrement={(productId) => setCart((current) => incrementCartLine(current, productId).lines)}
          onDecrement={(productId) => setCart((current) => decrementCartLine(current, productId).lines)}
          onRemove={(productId) => setCart((current) => removeCartLine(current, productId).lines)}
          onClear={clearTicket}
          onHold={holdActiveTicket}
          onRestoreHeldCart={restoreHeldTicket}
          onDiscardHeldCart={discardHeldTicket}
          onCheckout={() => void openCheckout()}
        />
      </div>

      <PosPaymentPanel
        open={paymentOpen}
        lines={cart}
        state={checkoutState}
        error={checkoutError}
        paymentMethod={paymentMethod}
        cashReceivedCents={cashReceivedCents}
        clientRequestId={clientRequestId}
        onPaymentMethod={setPaymentMethod}
        onCashReceivedCents={setCashReceivedCents}
        onClose={() => setPaymentOpen(false)}
        onConfirm={() => void confirmSale()}
      />

      <PosSaleSuccess sale={lastReceipt} onNewSale={clearTicket} />
    </PrismaTabletShellUnified>
  );
}
