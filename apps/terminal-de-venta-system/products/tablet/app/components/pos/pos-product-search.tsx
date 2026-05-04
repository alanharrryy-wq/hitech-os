"use client";

import type { FormEvent } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { UiState } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import styles from "./pos.module.css";

/* PRISMA_POS_VISUAL_SURFACE_LOCK_260503
 * Search is a control layer, not the visual protagonist. It exposes live catalog
 * counts while staying quieter than product cards and COBRAR.
 */

function stateCopy(state?: UiState) {
  if (state === "loading") return "Consultando catálogo";
  if (state === "error") return "Catálogo requiere revisión";
  if (state === "empty") return "Sin coincidencias";
  if (state === "ready") return "Catálogo listo";
  return "Búsqueda local";
}

export function PosProductSearch({
  query,
  setQuery,
  loading,
  error,
  resultCount,
  activeCount,
  state,
  onSearch,
  onResolve,
  onClear
}: {
  query: string;
  setQuery: (value: string) => void;
  loading: boolean;
  error: unknown;
  resultCount?: number;
  activeCount?: number;
  state?: UiState;
  onSearch: () => void;
  onResolve: () => void;
  onClear: () => void;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className={styles.searchCard} onSubmit={submit} data-prisma-component="SearchBar">
      <label className={styles.searchLabel}>
        <span>Buscar o escanear</span>
        <div className={styles.searchInputWrap}>
          <PrismaIcon name="search" size={22} />
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Nombre, SKU o código de barras"
            type="search"
          />
        </div>
      </label>

      <div className={styles.catalogInsight} aria-live="polite">
        <span>{stateCopy(state)}</span>
        <strong>{activeCount ?? 0} activos</strong>
        <small>{resultCount ?? 0} visibles</small>
      </div>

      <div className={styles.searchActions}>
        <button className={styles.primaryButton} type="submit" disabled={loading} data-prisma-component="IconButton">
          Buscar
        </button>
        <button className={styles.secondaryButton} type="button" onClick={onResolve} disabled={loading || !query.trim()} data-prisma-component="ScanButton">
          <PrismaIcon name="scan" size={18} />
          Resolver código
        </button>
        <button className={styles.ghostButton} type="button" onClick={onClear} disabled={loading} data-prisma-component="IconButton">
          Limpiar
        </button>
      </div>
      <PosErrorBanner error={error} />
    </form>
  );
}
