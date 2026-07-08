"use client";

import { useState, type FormEvent } from "react";
import { clsx, type ClassValue } from "clsx";
import { Loader2, RefreshCcw, Search, Sparkles } from "lucide-react";
import { motion } from "motion/react";
import { twMerge } from "tailwind-merge";
import type { UiState } from "@/lib/pos/cart-state";
import { PosErrorBanner } from "./pos-error-banner";
import styles from "./pos.module.css";

/* PRISMA_POS_VISUAL_SURFACE_LOCK_260503
 * Search is a control layer, not the visual protagonist. It exposes live catalog
 * counts while staying quieter than product cards and COBRAR.
 */

function stateCopy(state?: UiState) {
  if (state === "loading") return "Buscando productos";
  if (state === "error") return "Revisa productos";
  if (state === "empty") return "Sin coincidencias";
  if (state === "ready") return "Productos listos";
  return "Buscar producto";
}

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(...inputs));
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
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch();
  }

  const [searchFocused, setSearchFocused] = useState(false);
  const searchExpanded = searchFocused || Boolean(query.trim()) || loading || Boolean(error);
  const searchInputId = "tablet-pos-product-search";
  const searchResultsId = "tablet-pos-product-results";

  return (
    <motion.form
      className={cn(styles.posPremiumSearchCard, Boolean(error) && styles.posPremiumSearchCardError)}
      onSubmit={submit}
      onFocusCapture={() => setSearchFocused(true)}
      onBlurCapture={(event: FormBlurEvent) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
          setSearchFocused(false);
        }
      }}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      data-prisma-component="SearchBar"
      data-prisma-panel="tablet.pos.search-card"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-pos-search"
      data-prisma-role="search-command"
      data-prisma-priority="primary"
      data-prisma-state={loading ? "loading" : error ? "error" : state ?? "idle"}
      data-prisma-motion="reduced-motion-safe"
      data-prisma-qa="tablet-qa-search"
      data-prisma-search-expanded={searchExpanded ? "true" : "false"}
      data-prisma-search-density="05C"
      aria-expanded={searchExpanded}
      aria-controls={searchResultsId}
    >
      <label className={styles.posPremiumSearchLabel} htmlFor={searchInputId}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-product-search"
        data-target="pos-product-search-search-90"
        data-kind="search"
        data-role="search-control"
      >
        <span
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-product-search"
          data-target="pos-product-search-search-91"
          data-kind="search"
          data-role="search-control"
        ><Sparkles aria-hidden="true" size={15} /> Buscar o escanear</span>
        <div className={styles.posPremiumSearchInputWrap} data-prisma-qa="tablet-qa-focus"
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-product-search"
          data-target="pos-product-search-search-92"
          data-kind="search"
          data-role="search-control"
        >
          {loading ? <Loader2 className={styles.posPremiumSpin} aria-hidden="true" size={22} /> : <Search aria-hidden="true" size={22} />}
          <input
            id={searchInputId}
            value={query}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="pos-product-search"
            data-target="pos-product-search-search-94"
            data-kind="search"
            data-role="search-control"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar producto o escanear código"
            type="search"
            aria-controls={searchResultsId}
          />
        </div>
      </label>

      <div className={styles.posPremiumCatalogInsight} aria-live="polite"
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-product-search"
        data-target="pos-product-search-search-105"
        data-kind="search"
        data-role="search-control"
      >
        <span
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="pos-product-search"
          data-target="pos-product-search-search-106"
          data-kind="search"
          data-role="search-control"
        >{stateCopy(state)}</span>
        <small>{resultCount ?? 0} productos</small>
      </div>

      <div className={styles.posPremiumSearchActions}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-product-search"
        data-target="pos-product-search-button-110"
        data-kind="button"
        data-role="search-control"
      >
        <motion.button
          className={styles.posPremiumPrimaryButton}
          type="submit"
          disabled={loading}
          whileTap={loading ? undefined : { scale: 0.98 }}
          whileHover={loading ? undefined : { y: -1 }}
          data-prisma-component="IconButton"
          data-prisma-role="primary-action"
          data-prisma-priority="primary"
          data-prisma-state={loading ? "loading" : "ready"}
          data-prisma-motion="press-feedback"
        >
          {loading ? <Loader2 className={styles.posPremiumSpin} aria-hidden="true" size={17} /> : <Search aria-hidden="true" size={17} />}
          Buscar
        </motion.button>
        <motion.button
          className={styles.posPremiumGhostButton}
          type="button"
          onClick={onClear}
          disabled={loading}
          whileTap={loading ? undefined : { scale: 0.98 }}
          whileHover={loading ? undefined : { y: -1 }}
          data-prisma-component="IconButton"
        >
          <RefreshCcw aria-hidden="true" size={17} />
          Limpiar
        </motion.button>
      </div>
      <PosErrorBanner error={error} />
    </motion.form>
  );
}
