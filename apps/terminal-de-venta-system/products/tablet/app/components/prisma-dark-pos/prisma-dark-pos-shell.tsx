"use client";

import { useState } from "react";
import { PrismaCartPanel } from "./prisma-cart-panel";
import { PrismaCategoryRail } from "./prisma-category-rail";
import { PrismaProductGrid } from "./prisma-product-grid";
import { PrismaSearchRow } from "./prisma-search-row";
import { PrismaSidebar } from "./prisma-sidebar";
import { PrismaTopActionBar } from "./prisma-top-action-bar";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

function emitPageAction(page: number) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("prisma:pos-product-page", {
    detail: { page, source: "prisma-dark-pos-shell", ts: new Date().toISOString() }
  }));
}

export function PrismaDarkPosShell() {
  const [activePage, setActivePage] = useState(1);
  const goToPage = (page: number) => {
    const nextPage = Math.min(5, Math.max(1, page));
    setActivePage(nextPage);
    emitPageAction(nextPage);
  };

  return (
    <div className={styles.screen} data-prisma-hardening="shell-pagination-260611">
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
          <button className={styles.pageArrow} type="button" aria-label="Página anterior" onClick={() => goToPage(activePage - 1)} disabled={activePage === 1}>
            <PrismaIcon name="arrow-left" size={18} />
          </button>
          {[1, 2, 3, 4, 5].map((page) => (
            <button key={page} className={page === activePage ? styles.pageActive : styles.pageNumber} type="button" aria-current={page === activePage ? "page" : undefined} onClick={() => goToPage(page)}>
              {page}
            </button>
          ))}
          <button className={styles.pageArrow} type="button" aria-label="Página siguiente" onClick={() => goToPage(activePage + 1)} disabled={activePage === 5}>
            <PrismaIcon name="arrow-right" size={18} />
          </button>
        </nav>
      </main>

      <PrismaCartPanel />
    </div>
  );
}
