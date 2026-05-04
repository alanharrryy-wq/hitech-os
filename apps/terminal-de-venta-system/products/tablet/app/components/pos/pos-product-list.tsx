"use client";

import { useEffect, useMemo, useState } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { PosProduct, UiState } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import { resolveProductPackshot } from "./pos-packshots";
import styles from "./pos.module.css";

/* PRISMA_POS_VISUAL_SURFACE_LOCK_260503
 * Product cards are part of the governed POS surface. Keep product foreground,
 * packshot fallback and price hierarchy aligned with pos.module.css tokens.
 */

function cx(...names: Array<string | false | null | undefined>) {
  return names.filter(Boolean).join(" ");
}

function productInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

function productVisual(product: PosProduct) {
  const source = product.name.toLowerCase();
  if (source.includes("coca") || source.includes("refresco")) return { shape: styles.figureBottle, label: "COLA", detail: "600 ml" };
  if (source.includes("agua") || source.includes("ciel")) return { shape: styles.figureBottleBlue, label: "CIEL", detail: "1 L" };
  if (source.includes("sabrita") || source.includes("papa")) return { shape: styles.figureBag, label: "SAB", detail: "45 g" };
  if (source.includes("lala") || source.includes("leche")) return { shape: styles.figureCarton, label: "LALA", detail: "1 L" };
  if (source.includes("nesc")) return { shape: styles.figureJar, label: "NES", detail: "200 g" };
  if (source.includes("bimbo") || source.includes("pan")) return { shape: styles.figureBread, label: "BIM", detail: "Pan" };
  if (source.includes("ace") || source.includes("deterg")) return { shape: styles.figureBox, label: "ACE", detail: "1 kg" };
  if (source.includes("zucar") || source.includes("cereal")) return { shape: styles.figureBoxBlue, label: "ZUC", detail: "730 g" };
  return { shape: styles.figureGeneric, label: productInitials(product.name) || "PR", detail: product.category ?? "SKU" };
}

function productStageTone(product: PosProduct) {
  const source = `${product.category ?? ""} ${product.name}`.toLowerCase();
  if (source.includes("beb") || source.includes("agua") || source.includes("ciel") || source.includes("refresco")) return styles.stageCool;
  if (source.includes("limp") || source.includes("hogar")) return styles.stageClean;
  if (source.includes("pan") || source.includes("dulce")) return styles.stageWarm;
  return styles.stageGold;
}

function productStockState(product: PosProduct) {
  if (!product.isActive) return "inactive";
  if (product.stockOnHand <= 0) return "empty";
  if (product.stockOnHand <= (product.lowStockThreshold ?? 5)) return "low";
  return "ok";
}

function stockCopy(product: PosProduct) {
  const state = productStockState(product);
  if (state === "inactive") return "Inactivo";
  if (state === "empty") return "Sin stock";
  if (state === "low") return `${product.stockOnHand} bajos`;
  return `${product.stockOnHand} disp.`;
}

function ProductMedia({ product }: { product: PosProduct }) {
  const visual = productVisual(product);
  const packshot = resolveProductPackshot(product.name, product.category, product.sku);
  const stageTone = productStageTone(product);

  return (
    <div
      className={cx(styles.productImageStage, stageTone, packshot && styles.stageHasPackshot)}
      data-prisma-component="ProductImageStage"
      data-prisma-packshot-host={packshot ? "true" : undefined}
      aria-hidden="true"
    >
      <span className={styles.productAura} />
      <span className={styles.productPedestal} />
      {packshot ? (
        <>
          <span className={cx(styles.productFigure, styles.productFigureFallback, visual.shape)} aria-hidden="true">
            <span className={styles.figureStripe} />
            <strong>{visual.label}</strong>
            <small>{visual.detail}</small>
          </span>
          <img
            className={cx(styles.productPackshot, styles[`productPackshot_${packshot.kind}`])}
            src={packshot.src}
            alt=""
            loading="lazy"
            draggable={false}
            onError={(event) => {
              event.currentTarget.closest("[data-prisma-packshot-host]")?.setAttribute("data-packshot-error", "true");
            }}
            onLoad={(event) => {
              event.currentTarget.closest("[data-prisma-packshot-host]")?.removeAttribute("data-packshot-error");
            }}
          />
        </>
      ) : (
        <span className={cx(styles.productFigure, visual.shape)}>
          <span className={styles.figureStripe} />
          <strong>{visual.label}</strong>
          <small>{visual.detail}</small>
        </span>
      )}
    </div>
  );
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
  const pageSize = 8;
  const [page, setPage] = useState(1);
  const pageCount = Math.max(1, Math.ceil(products.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const pageProducts = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return products.slice(start, start + pageSize);
  }, [currentPage, products]);
  const firstVisible = products.length ? (currentPage - 1) * pageSize + 1 : 0;
  const lastVisible = products.length ? Math.min(products.length, currentPage * pageSize) : 0;

  useEffect(() => {
    setPage(1);
  }, [products]);
  if (state === "loading") {
    return (
      <div className={styles.statePanel} data-prisma-component="EmptyState">
        <PrismaIcon name="package" size={24} />
        <strong>Cargando catálogo local</strong>
        <span>Consultando productos de la Tablet.</span>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className={styles.statePanel} data-prisma-component="ErrorState">
        <PosErrorBanner error={error} />
      </div>
    );
  }

  if (!products.length) {
    return (
      <div className={styles.statePanel} data-prisma-component="EmptyState">
        <PrismaIcon name="package" size={24} />
        <strong>No hay productos para mostrar</strong>
        <span>Busca por nombre, SKU o código de barras.</span>
      </div>
    );
  }

  return (
    <>
      <section className={styles.productGrid} aria-label="Productos encontrados" data-prisma-component="ProductGrid">
        {pageProducts.map((product) => {
          const stockState = productStockState(product);
          const disabled = !product.isActive || product.stockOnHand <= 0;
          return (
            <article
              key={product.id}
              className={cx(styles.productCard, disabled && styles.productCardDisabled)}
              data-prisma-component="ProductCard"
              data-prisma-stock-state={stockState}
            >
              <div className={styles.productCardTop}>
                <span className={cx(styles.productStatusPill, stockState === "ok" && styles.productStatusOk, stockState === "low" && styles.productStatusWarn, (stockState === "empty" || stockState === "inactive") && styles.productStatusDanger)}>
                  {stockCopy(product)}
                </span>
                <span className={styles.favoriteStar} data-prisma-component="FavoriteStar" aria-hidden="true">★</span>
              </div>

              <ProductMedia product={product} />

              <div className={styles.productText}>
                <strong className={styles.productName}>{product.name}</strong>
                <span className={styles.productSku}>SKU {product.sku}</span>
                {product.barcode ? <span className={styles.productBarcode}>CB {product.barcode}</span> : null}
                <div className={styles.productMetaRail}>
                  <span className={product.isActive ? styles.badgeOk : styles.badgeDanger}>{product.isActive ? "Activo" : "Inactivo"}</span>
                  {product.category ? <span className={styles.badgeNeutral}>{product.category}</span> : null}
                </div>
              </div>

              <div className={styles.productAside}>
                <span className={cx(styles.productPriceStack, styles.productPrice)}>
                  <strong className={styles.priceValue}>{formatMoney(product.priceCents)}</strong>
                  <small>MXN</small>
                </span>
                <button
                  className={styles.addButton}
                  type="button"
                  onClick={() => onAdd(product)}
                  disabled={disabled}
                  data-prisma-component="IconButton"
                >
                  <PrismaIcon name="plus" size={18} />
                  Agregar
                </button>
              </div>
            </article>
          );
        })}
      </section>

      <nav className={styles.pagination} aria-label="Paginación de productos" data-prisma-component="Pagination">
        <span className={styles.paginationSummary}>Mostrando {firstVisible}-{lastVisible} de {products.length}</span>
        <button type="button" disabled={currentPage <= 1} aria-label="Página anterior" onClick={() => setPage((value) => Math.max(1, value - 1))}>
          <PrismaIcon name="arrow-left" size={18} />
        </button>
        {Array.from({ length: pageCount }, (_, index) => index + 1).slice(0, 9).map((pageNumber) => (
          <button
            key={`catalog-page-${pageNumber}`}
            className={pageNumber === currentPage ? styles.pageActive : undefined}
            type="button"
            aria-current={pageNumber === currentPage ? "page" : undefined}
            onClick={() => setPage(pageNumber)}
          >
            {pageNumber}
          </button>
        ))}
        {pageCount > 9 ? <span className={styles.paginationMore}>… {pageCount}</span> : null}
        <button type="button" disabled={currentPage >= pageCount} aria-label="Página siguiente" onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>
          <PrismaIcon name="arrow-right" size={18} />
        </button>
      </nav>
    </>
  );
}
