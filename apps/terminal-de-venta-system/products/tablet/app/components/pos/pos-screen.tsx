"use client";

import { useEffect, useState } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import type { CartLine, PosProduct, UiState } from "@/lib/pos/cart-state";
import { readCartFromStorage, requestJson, writeCartToStorage } from "@/lib/pos/cart-state";
import { PosProductSearch } from "./pos-product-search";
import { PosProductList } from "./pos-product-list";
import { PosTicketPanel } from "./pos-ticket-panel";
import { PosShortcuts } from "./pos-shortcuts";
import styles from "./pos.module.css";

export function PosScreen() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<PosProduct[]>([]);
  const [productState, setProductState] = useState<UiState>("idle");
  const [productError, setProductError] = useState<unknown>(null);
  const [cart, setCart] = useState<CartLine[]>([]);

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

  function addProduct(product: PosProduct) {
    setCart((current) => {
      const existing = current.find((line) => line.product.id === product.id);
      if (existing) return current.map((line) => line.product.id === product.id ? { ...line, qty: line.qty + 1 } : line);
      return [...current, { product, qty: 1 }];
    });
  }

  function increment(productId: string) {
    setCart((current) => current.map((line) => line.product.id === productId ? { ...line, qty: line.qty + 1 } : line));
  }

  function decrement(productId: string) {
    setCart((current) => current.flatMap((line) => {
      if (line.product.id !== productId) return [line];
      if (line.qty <= 1) return [];
      return [{ ...line, qty: line.qty - 1 }];
    }));
  }

  useEffect(() => {
    setCart(readCartFromStorage());
    void loadProducts("");
  }, []);

  useEffect(() => {
    writeCartToStorage(cart);
  }, [cart]);

  return (
    <PrismaTabletShellUnified
      currentPath="/pos"
      title="Vender"
      subtitle="Busca, escanea, agrega productos y manda el ticket a cobro sin rodeos raros."
      status={<TabletShellStatusPill tone="ok">Venta local activa</TabletShellStatusPill>}
      actions={<PosShortcuts />}
    >
      <div className={styles.posWorkspace}>
        <section className={styles.catalogArea} aria-label="Catálogo de venta">
          <PosProductSearch
            query={query}
            setQuery={setQuery}
            loading={productState === "loading"}
            error={productError}
            onSearch={() => void loadProducts(query)}
            onResolve={() => void resolveCode()}
            onClear={() => { setQuery(""); void loadProducts(""); }}
          />
          <PosProductList products={products} state={productState} error={productError} onAdd={addProduct} />
        </section>
        <PosTicketPanel
          lines={cart}
          onIncrement={increment}
          onDecrement={decrement}
          onRemove={(productId) => setCart((current) => current.filter((line) => line.product.id !== productId))}
          onClear={() => setCart([])}
        />
      </div>
    </PrismaTabletShellUnified>
  );
}
