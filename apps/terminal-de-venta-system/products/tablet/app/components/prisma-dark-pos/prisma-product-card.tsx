import type { Product } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

type PrismaProductCardProps = {
  product: Product;
};

export function PrismaProductCard({ product }: PrismaProductCardProps) {
  return (
    <article className={styles.productCard}>
      <div className={styles.productCardTop}>
        <button className={product.favorite ? styles.favoriteActive : styles.favoriteButton} type="button" aria-label="Favorito">
          <PrismaIcon name="star" size={17} />
        </button>
      </div>

      <ProductFigure product={product} />

      <div className={styles.productInfo}>
        <h2>{product.name}</h2>
        <strong>{product.price}</strong>
        <span>{product.stock}</span>
      </div>
    </article>
  );
}

export function ProductFigure({ product, compact = false }: { product: Product; compact?: boolean }) {
  const className = [
    compact ? styles.productStageCompact : styles.productStage,
    styles[`glow_${product.glow}`]
  ].join(" ");

  const figureClassName = [
    styles.productFigure,
    styles[`shape_${product.shape}`],
    styles[`tone_${product.visual}`],
    compact ? styles.productFigureCompact : ""
  ].join(" ");

  return (
    <div className={className} aria-hidden="true">
      <span className={styles.productAura} />
      <div className={figureClassName}>
        <span className={styles.figureStripe} />
        <span className={styles.figureLabel}>{product.badge}</span>
        <span className={styles.figureDetail}>{product.detail}</span>
      </div>
      <span className={styles.productPedestal} />
    </div>
  );
}
