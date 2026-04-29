"use client";

import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { PosProduct, UiState } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import styles from "./pos.module.css";

function StockBadge({ product }: { product: PosProduct }) {
  const low = product.stockOnHand <= (product.lowStockThreshold ?? 5);
  return <span className={low ? styles.badgeWarn : styles.badgeNeutral}>{product.stockOnHand} existencias</span>;
}

export function PosProductList({
  products,
  state,
  error,
  onAdd
}: {
  products: PosProduct[];
  state: UiState;
  error: unknown;
  onAdd: (product: PosProduct) => void;
}) {
  if (state === "loading") {
    return <div className={styles.statePanel}><PrismaIcon name="package" size={24} /><strong>Cargando catálogo local</strong><span>Consultando productos de la Tablet.</span></div>;
  }
  if (state === "error") {
    return <div className={styles.statePanel}><PosErrorBanner error={error} /></div>;
  }
  if (!products.length) {
    return <div className={styles.statePanel}><PrismaIcon name="package" size={24} /><strong>No hay productos para mostrar</strong><span>Busca por nombre, SKU o código de barras.</span></div>;
  }

  return (
    <section className={styles.productList} aria-label="Productos encontrados">
      {products.map((product) => (
        <article key={product.id} className={styles.productRow}>
          <div className={styles.productIcon}><PrismaIcon name="package" size={24} /></div>
          <div className={styles.productText}>
            <strong>{product.name}</strong>
            <span>{product.sku}{product.barcode ? ` · ${product.barcode}` : ""}</span>
            <div className={styles.rowSignals}>
              <span className={product.isActive ? styles.badgeOk : styles.badgeDanger}>{product.isActive ? "Activo" : "Inactivo"}</span>
              <StockBadge product={product} />
            </div>
          </div>
          <div className={styles.productAside}>
            <strong>{formatMoney(product.priceCents)}</strong>
            <button className={styles.addButton} type="button" onClick={() => onAdd(product)} disabled={!product.isActive || product.stockOnHand <= 0}>
              <PrismaIcon name="plus" size={18} />
              Agregar
            </button>
          </div>
        </article>
      ))}
    </section>
  );
}
