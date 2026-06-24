"use client";

import { useEffect, useMemo, useState } from "react";
import { cva } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import { AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight, PackageSearch, Plus, Star } from "lucide-react";
import { motion } from "motion/react";
import { twMerge } from "tailwind-merge";
import type { PosProduct, UiState } from "@/lib/pos/cart-state";
import { formatMoney } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import { resolveNextPackshotSrc, resolveProductPackshot } from "./pos-packshots";
import { usePrismaPackshotSkin } from "./use-prisma-packshot-skin";
import styles from "./pos.module.css";

/* PRISMA_POS_VISUAL_SURFACE_LOCK_260503
 * Product cards are part of the governed POS surface. Keep product foreground,
 * packshot fallback and price hierarchy aligned with pos.module.css tokens.
 */

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(...inputs));
}

const productCardChrome = cva(styles.posPremiumProductCard, {
  variants: {
    disabled: {
      true: styles.posPremiumProductCardDisabled,
      false: null
    },
    stock: {
      ok: styles.posPremiumProductStockOk,
      low: styles.posPremiumProductStockLow,
      empty: styles.posPremiumProductStockEmpty,
      inactive: styles.posPremiumProductStockEmpty
    }
  },
  defaultVariants: {
    disabled: false,
    stock: "ok"
  }
});

const addButtonChrome = cva(styles.posPremiumAddButton, {
  variants: {
    disabled: {
      true: styles.posPremiumAddButtonDisabled,
      false: null
    }
  },
  defaultVariants: {
    disabled: false
  }
});

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
  const packshotSkin = usePrismaPackshotSkin();
  const packshot = resolveProductPackshot(product.name, product.category, product.sku, { skin: packshotSkin });
  const stageTone = productStageTone(product);

  return (
    <div
      className={cn(styles.posPremiumProductStage, stageTone, packshot && styles.stageHasPackshot)}
      data-prisma-component="ProductImageStage"
      data-prisma-packshot-host={packshot ? "true" : undefined}
      aria-hidden="true"
    >
      <span className={styles.productAura} />
      <span className={styles.productPedestal} />
      {packshot ? (
        <>
          <span className={cn(styles.productFigure, styles.productFigureFallback, visual.shape)} aria-hidden="true">
            <span className={styles.figureStripe} />
            <strong>{visual.label}</strong>
            <small>{visual.detail}</small>
          </span>
          <img
            className={cn(styles.productPackshot, styles[`productPackshot_${packshot.kind}`])}
            src={packshot.src}
            alt=""
            loading="lazy"
            draggable={false}
            onError={(event: { currentTarget: HTMLImageElement }) => {
              const nextSrc = resolveNextPackshotSrc(event.currentTarget.src, packshot.fallbackSrcs);
              if (nextSrc) {
                event.currentTarget.src = nextSrc;
                return;
              }
              event.currentTarget.closest("[data-prisma-packshot-host]")?.setAttribute("data-packshot-error", "true");
            }}
            onLoad={(event: { currentTarget: HTMLImageElement }) => {
              event.currentTarget.closest("[data-prisma-packshot-host]")?.removeAttribute("data-packshot-error");
            }}
          />
        </>
      ) : (
        <span className={cn(styles.productFigure, visual.shape)}>
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
  query,
  newProductHref,
  canAddProduct = true,
  blockedReason,
  onAdd,
  onSearchAgain,
  onCancelSearch
}: {
  products: PosProduct[];
  state: UiState;
  error: unknown;
  query: string;
  newProductHref: string;
  canAddProduct?: boolean;
  blockedReason?: string;
  onAdd: (product: PosProduct) => void;
  onSearchAgain: () => void;
  onCancelSearch: () => void;
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
      <div className={styles.posPremiumStatePanel} data-prisma-component="EmptyState" data-prisma-zone="tablet-pos-empty-state" data-prisma-state="loading" data-prisma-motion="reduced-motion-safe">
        <PackageSearch aria-hidden="true" size={26} />
        <strong>Cargando catálogo local</strong>
        <span>Consultando productos de la Tablet.</span>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className={styles.posPremiumStatePanel} data-prisma-component="ErrorState" data-prisma-zone="tablet-pos-error-state" data-prisma-state="error" data-prisma-motion="error-feedback">
        <AlertTriangle aria-hidden="true" size={24} />
        <PosErrorBanner error={error} />
      </div>
    );
  }

  if (!products.length) {
    const searched = query.trim();
    return (
      <div className={styles.posPremiumStatePanel} data-prisma-component="EmptyState" data-prisma-zone="tablet-pos-empty-state" data-prisma-state="empty" data-prisma-motion="reduced-motion-safe">
        <PackageSearch aria-hidden="true" size={26} />
        <strong>{searched ? "Producto no encontrado." : "No hay productos para mostrar"}</strong>
        <span>
          {searched
            ? `No encontramos "${searched}" en el catálogo local. Puedes registrarlo ahora, buscar de nuevo o cancelar esta búsqueda.`
            : "Busca por nombre, SKU o código de barras."}
        </span>
        {searched ? (
          <div className={styles.posPremiumEmptyActions}>
            <a className={styles.posPremiumPrimaryButton} href={newProductHref}>Registrar producto nuevo</a>
            <button className={styles.posPremiumSecondaryButton} type="button" onClick={onSearchAgain}>Buscar de nuevo</button>
            <button className={styles.posPremiumGhostButton} type="button" onClick={onCancelSearch}>Cancelar</button>
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <>
      <section
        className={styles.posPremiumProductGrid}
        aria-label="Productos encontrados"
        data-prisma-component="ProductGrid"
        data-prisma-panel="tablet.pos.product-grid"
        data-prisma-surface="tablet"
        data-prisma-route="/pos"
        data-prisma-zone="tablet-pos-product-grid"
        data-prisma-role="operational-summary"
        data-prisma-priority="primary"
        data-prisma-qa="tablet-qa-product-card"
      >
        {pageProducts.map((product, index) => {
          const stockState = productStockState(product);
          const disabled = !canAddProduct || !product.isActive || product.stockOnHand <= 0;
          return (
            <motion.article
              key={product.id}
              className={productCardChrome({ disabled, stock: stockState })}
              initial={{ opacity: 0, y: 12, scale: 0.988 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              whileHover={disabled ? undefined : { y: -5, scale: 1.012 }}
              transition={{ duration: 0.2, delay: Math.min(index * 0.026, 0.18), ease: [0.22, 1, 0.36, 1] }}
              data-prisma-component="ProductCard"
              data-prisma-zone="tablet-pos-product-card"
              data-prisma-role="product-card"
              data-prisma-priority="primary"
              data-prisma-motion={disabled ? "reduced-motion-safe" : "hover-lift"}
              data-prisma-qa="tablet-qa-product-card"
              data-prisma-stock-state={stockState}
              data-prisma-state={disabled ? "disabled" : stockState}
            >
              <div className={styles.posPremiumProductCardTop}>
                <span className={cn(styles.posPremiumProductStatus, stockState === "ok" && styles.posPremiumProductStatusOk, stockState === "low" && styles.posPremiumProductStatusWarn, (stockState === "empty" || stockState === "inactive") && styles.posPremiumProductStatusDanger)}>
                  {stockState === "ok" ? <CheckCircle2 aria-hidden="true" size={13} /> : null}
                  {stockCopy(product)}
                </span>
                <span className={styles.posPremiumFavoriteStar} data-prisma-component="FavoriteStar" aria-hidden="true">
                  <Star size={16} fill="currentColor" />
                </span>
              </div>

              <ProductMedia product={product} />

              <div className={styles.posPremiumProductText}>
                <strong className={styles.posPremiumProductName}>{product.name}</strong>
                <div className={styles.posPremiumProductMetaRail}>
                  <span className={product.isActive ? styles.badgeOk : styles.badgeDanger}>{product.isActive ? "Activo" : "Inactivo"}</span>
                  {product.category ? <span className={styles.badgeNeutral}>{product.category}</span> : null}
                </div>
              </div>

              <div className={styles.posPremiumProductAside}>
                <span className={styles.posPremiumProductPrice}>
                  <strong>{formatMoney(product.priceCents)}</strong>
                  <small>MXN</small>
                </span>
                <motion.button
                  className={addButtonChrome({ disabled })}
                  type="button"
                  onClick={() => onAdd(product)}
                  disabled={disabled}
                  whileTap={disabled ? undefined : { scale: 0.972 }}
                  whileHover={disabled ? undefined : { y: -1 }}
                  title={!canAddProduct ? blockedReason ?? "Abre turno antes de agregar productos." : undefined}
                  data-prisma-component="IconButton"
                  data-prisma-zone="tablet-pos-product-add"
                  data-prisma-role="primary-action"
                  data-prisma-priority={disabled ? "passive" : "primary"}
                  data-prisma-motion="press-feedback"
                  data-prisma-state={disabled ? "disabled" : "ready"}
                  data-prisma-qa={disabled ? "tablet-qa-disabled" : undefined}
                >
                  <Plus aria-hidden="true" size={18} />
                  {canAddProduct ? "Agregar" : "Caja cerrada"}
                </motion.button>
              </div>
            </motion.article>
          );
        })}
      </section>

      <nav className={styles.posPremiumPagination} aria-label="Paginación de productos" data-prisma-component="Pagination">
        <span className={styles.paginationSummary}>Mostrando {firstVisible}-{lastVisible} de {products.length}</span>
        <button type="button" disabled={currentPage <= 1} aria-label="Página anterior" onClick={() => setPage((value) => Math.max(1, value - 1))}>
          <ChevronLeft aria-hidden="true" size={18} />
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
          <ChevronRight aria-hidden="true" size={18} />
        </button>
      </nav>
    </>
  );
}
