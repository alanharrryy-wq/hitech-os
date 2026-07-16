"use client";

import { useState, type FormEvent } from "react";
import { Loader2, Search, X } from "lucide-react";
import type { UiState } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import styles from "./pos.module.css";

function stateCopy(state?: UiState) {
  if (state === "loading") return "Buscando";
  if (state === "error") return "Revisa el catálogo";
  if (state === "empty") return "Sin coincidencias";
  if (state === "ready") return "Catálogo listo";
  return "Catálogo local";
}

type FormBlurEvent = FormEvent<HTMLFormElement> & {
  relatedTarget: EventTarget | null;
};

export function PosProductSearch({
  query,
  setQuery,
  loading,
  error,
  resultCount,
  state,
  onSearch,
  onClear
}: {
  query: string;
  setQuery: (value: string) => void;
  loading: boolean;
  error: unknown;
  resultCount?: number;
  state?: UiState;
  onSearch: () => void;
  onClear: () => void;
}) {
  const [searchFocused, setSearchFocused] = useState(false);
  const searchExpanded = searchFocused || Boolean(query.trim()) || loading || Boolean(error);
  const searchInputId = "tablet-pos-product-search";
  const searchResultsId = "tablet-pos-product-results";

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  return (
    <form
      className={`${styles.posPremiumSearchCard} ${error ? styles.posPremiumSearchCardError : ""}`}
      onSubmit={submit}
      onFocusCapture={() => setSearchFocused(true)}
      onBlurCapture={(event: FormBlurEvent) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setSearchFocused(false);
      }}
      data-prisma-component="SearchBar"
      data-prisma-panel="tablet.pos.search-card"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-pos-search"
      data-prisma-role="search-command"
      data-prisma-priority="primary"
      data-prisma-state={loading ? "loading" : error ? "error" : state ?? "idle"}
      data-prisma-qa="tablet-qa-search"
      data-prisma-search-expanded={searchExpanded ? "true" : "false"}
      aria-expanded={searchExpanded}
      aria-controls={searchResultsId}
    >
      <label className={styles.posPremiumSearchLabel} htmlFor={searchInputId}>
        <span className={styles.visuallyHidden}>Buscar producto o escanear código</span>
        {loading ? <Loader2 className={styles.posPremiumSpin} aria-hidden="true" size={21} /> : <Search aria-hidden="true" size={21} />}
        <input
          id={searchInputId}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar producto o escanear código"
          type="search"
          aria-controls={searchResultsId}
          autoComplete="off"
        />
        {query ? (
          <button className={styles.posPremiumSearchClear} type="button" onClick={onClear} disabled={loading} aria-label="Limpiar búsqueda">
            <X aria-hidden="true" size={18} />
          </button>
        ) : null}
      </label>

      <div className={styles.posPremiumCatalogInsight} aria-live="polite">
        <strong>{stateCopy(state)}</strong>
        <span>{resultCount ?? 0} productos</span>
      </div>
      <PosErrorBanner error={error} />
    </form>
  );
}
