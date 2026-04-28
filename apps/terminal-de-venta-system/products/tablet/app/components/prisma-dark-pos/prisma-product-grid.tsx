import { products } from "./prisma-dark-pos-data";
import { PrismaProductCard } from "./prisma-product-card";
import styles from "./prisma-dark-pos.module.css";

export function PrismaProductGrid() {
  return (
    <section className={styles.productGrid} aria-label="Catálogo de productos">
      {products.map((product) => (
        <PrismaProductCard key={product.id} product={product} />
      ))}
    </section>
  );
}
