import { PrismaCartPanel } from "./prisma-cart-panel";
import { PrismaCategoryRail } from "./prisma-category-rail";
import { PrismaProductGrid } from "./prisma-product-grid";
import { PrismaSearchRow } from "./prisma-search-row";
import { PrismaSidebar } from "./prisma-sidebar";
import { PrismaTopActionBar } from "./prisma-top-action-bar";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaDarkPosShell() {
  return (
    <div className={styles.screen}>
      <PrismaSidebar />

      <header className={styles.titleBar}>
        <h1>Ventas</h1>
      </header>

      <PrismaTopActionBar />

      <main className={styles.workspace} aria-label="Área de venta PRISMA">
        <PrismaSearchRow />
        <PrismaCategoryRail />
        <PrismaProductGrid />
        <nav className={styles.pagination} aria-label="Paginación de productos">
          <button className={styles.pageArrow} type="button" aria-label="Página anterior">
            <PrismaIcon name="arrow-left" size={18} />
          </button>
          {[1, 2, 3, 4, 5].map((page) => (
            <button key={page} className={page === 1 ? styles.pageActive : styles.pageNumber} type="button">
              {page}
            </button>
          ))}
          <button className={styles.pageArrow} type="button" aria-label="Página siguiente">
            <PrismaIcon name="arrow-right" size={18} />
          </button>
        </nav>
      </main>

      <PrismaCartPanel />
    </div>
  );
}
