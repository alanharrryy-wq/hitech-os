"use client";

import { useState } from "react";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

function emitSearchAction(action: string, query = "") {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("prisma:pos-search-action", {
    detail: { action, query, source: "prisma-dark-pos-search-row", ts: new Date().toISOString() }
  }));
}

export function PrismaSearchRow() {
  const [query, setQuery] = useState("");

  return (
    <section className={styles.searchRow} aria-label="Búsqueda de productos" data-prisma-hardening="search-actions-260611">
      <label className={styles.searchBox}>
        <PrismaIcon name="search" className={styles.searchLeadingIcon} size={22} />
        <input
          aria-label="Buscar producto"
          placeholder="Buscar producto por código, nombre o SKU..."
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              emitSearchAction("search", query);
            }
          }}
        />
        <PrismaIcon name="scan" className={styles.searchTrailingIcon} size={22} />
      </label>

      <button className={styles.scanButton} type="button" onClick={() => emitSearchAction("scan", query)}>
        <PrismaIcon name="scan" size={21} />
        <span>ESCANEAR</span>
      </button>

      <button className={styles.moreButton} type="button" aria-label="Más opciones" onClick={() => emitSearchAction("more-options", query)}>
        <PrismaIcon name="more" size={22} />
      </button>
    </section>
  );
}
