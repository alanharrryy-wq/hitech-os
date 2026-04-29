"use client";

import type { FormEvent } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { PosErrorBanner } from "./pos-error-banner";
import styles from "./pos.module.css";

export function PosProductSearch({
  query,
  setQuery,
  loading,
  error,
  onSearch,
  onResolve,
  onClear
}: {
  query: string;
  setQuery: (value: string) => void;
  loading: boolean;
  error: unknown;
  onSearch: () => void;
  onResolve: () => void;
  onClear: () => void;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form className={styles.searchCard} onSubmit={submit}>
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
      <div className={styles.searchActions}>
        <button className={styles.primaryButton} type="submit" disabled={loading}>
          Buscar
        </button>
        <button className={styles.secondaryButton} type="button" onClick={onResolve} disabled={loading || !query.trim()}>
          <PrismaIcon name="scan" size={18} />
          Resolver código
        </button>
        <button className={styles.ghostButton} type="button" onClick={onClear} disabled={loading}>
          Limpiar
        </button>
      </div>
      <PosErrorBanner error={error} />
    </form>
  );
}
