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
  const [selectedCategory, setSelectedCategory] = useState("Todas");
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [cashReceivedCents, setCashReceivedCents] = useState(0);
  const [checkoutState, setCheckoutState] = useState<CheckoutState>("idle");
  const [checkoutError, setCheckoutError] = useState<unknown>(null);
  const [clientRequestId, setClientRequestId] = useState("");
  const [lastReceipt, setLastReceipt] = useState<CompletedSaleReceipt | null>(null);

  const categories = useMemo(
    () => ["Todas", ...Array.from(new Set(products.map((product) => product.category?.trim()).filter(Boolean) as string[])).sort((a, b) => a.localeCompare(b, "es-MX"))],
    [products]
  );
  const visibleProducts = selectedCategory === "Todas" ? products : products.filter((product) => (product.category?.trim() || "General") === selectedCategory);
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
      visualSurface="tablet-pos-light-operational-00q"
      visualPreset="PRISMA_LIGHT_OPERATIONAL_POS"
    >
      <div className={styles.posWorkspace} data-prisma-golden-flow="touch-guided-sidebar-04i" data-prisma-light-operational="00Q" data-prisma-pos-live="00T" data-prisma-layer="surface">
        <PosLiveBinding />
        <span hidden data-prisma-golden-flow="touch-only-actions-04h" data-prisma-touch-only-actions="04H" />
        <section className={styles.catalogArea}>
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
          <nav className={styles.categoryRail}>
            {categories.map((category) => (
              <button
                key={category}
                className={category === selectedCategory ? styles.categoryButtonActive : styles.categoryButton}
                type="button"
                onClick={() => setSelectedCategory(category)}
                data-active={category === selectedCategory ? "true" : "false"}
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
