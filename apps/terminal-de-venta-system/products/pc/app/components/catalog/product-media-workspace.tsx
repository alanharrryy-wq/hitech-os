/* PRISMA_DARK_PACKSHOTS_197 */
"use client";

import { type FormEvent, useMemo, useState } from "react";
import styles from "./product-media-workspace.module.css";

type Product = { id: string; sku: string; name: string; mediaRef: string | null; updatedAt: string };
type Asset = {
  assetId: string;
  canonicalName: string;
  displayName: string;
  category: string;
  keywords: string[];
  runtimePath: string;
  thumbnailPath: string;
};
type Workspace = {
  products: Product[];
  library: Asset[];
  meta: {
    source: "canonical_prisma" | "unavailable";
    warning: string | null;
    generatedAt: string;
    libraryId: string;
    libraryCount: number;
  };
};
type MediaMode = "NONE" | "LIBRARY" | "CUSTOM";

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

function normalized(value: string) {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function inferMode(mediaRef: string | null): MediaMode {
  if (!mediaRef) return "NONE";
  return mediaRef.startsWith("/product-media/catalog/") ? "LIBRARY" : "CUSTOM";
}

export function ProductMediaWorkspace({ initialWorkspace }: { initialWorkspace: Workspace }) {
  const [products, setProducts] = useState(initialWorkspace.products);
  const [productId, setProductId] = useState("");
  const [productQuery, setProductQuery] = useState("");
  const [assetQuery, setAssetQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [mode, setMode] = useState<MediaMode>("NONE");
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [customRef, setCustomRef] = useState("");
  const [notice, setNotice] = useState(initialWorkspace.meta.warning ?? "");
  const [isSaving, setIsSaving] = useState(false);

  const selected = useMemo(() => products.find((product) => product.id === productId) ?? null, [products, productId]);
  const selectedAsset = useMemo(
    () => initialWorkspace.library.find((asset) => asset.assetId === selectedAssetId) ?? null,
    [initialWorkspace.library, selectedAssetId]
  );
  const categories = useMemo(
    () => Array.from(new Set(initialWorkspace.library.map((asset) => asset.category))).sort((a, b) => a.localeCompare(b, "es")),
    [initialWorkspace.library]
  );
  const productMatches = useMemo(() => {
    const needle = normalized(productQuery);
    return products
      .filter((product) => !needle || normalized(`${product.sku} ${product.name}`).includes(needle))
      .slice(0, 40);
  }, [products, productQuery]);
  const assetMatches = useMemo(() => {
    const needle = normalized(assetQuery);
    return initialWorkspace.library
      .filter((asset) => category === "all" || asset.category === category)
      .filter((asset) => !needle || normalized(`${asset.displayName} ${asset.category} ${asset.keywords.join(" ")}`).includes(needle))
      .slice(0, 60);
  }, [assetQuery, category, initialWorkspace.library]);

  function selectProduct(product: Product) {
    setProductId(product.id);
    setProductQuery(`${product.sku} · ${product.name}`);
    const nextMode = inferMode(product.mediaRef);
    setMode(nextMode);
    const matched = initialWorkspace.library.find((asset) => asset.runtimePath === product.mediaRef);
    setSelectedAssetId(matched?.assetId ?? "");
    setCustomRef(nextMode === "CUSTOM" ? product.mediaRef ?? "" : "");
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    const nextMediaRef = mode === "NONE" ? null : mode === "LIBRARY" ? selectedAsset?.runtimePath ?? null : customRef.trim() || null;
    if (mode === "LIBRARY" && !selectedAsset) {
      setNotice("Selecciona una imagen de la biblioteca antes de guardar.");
      return;
    }
    setIsSaving(true);
    setNotice("");
    try {
      const data = await readApi<{ product: Product }>(await fetch("/api/backoffice/product-media", {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ productId: selected.id, expectedUpdatedAt: selected.updatedAt, mediaRef: nextMediaRef })
      }));
      setProducts((current) => current.map((product) => product.id === data.product.id ? data.product : product));
      setNotice(data.product.mediaRef
        ? "Imagen guardada. El catálogo PC→Tablet proyectará la misma referencia portable."
        : "Imagen retirada. El POS conservará su fallback oscuro genérico.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "No fue posible guardar la referencia de imagen.");
    } finally {
      setIsSaving(false);
    }
  }

  const preview = mode === "LIBRARY" ? selectedAsset?.runtimePath : mode === "CUSTOM" ? customRef.trim() : "";

  return (
    <section className="card" data-prisma-component="ProductMediaWorkspace" data-prisma-surface="pc.catalog.media">
      <div className="section-head">
        <div>
          <div className="kicker">biblioteca oscura administrada</div>
          <h2 className="section-title">Imagen de producto</h2>
          <div className="section-copy">Busca un SKU, elige una imagen genérica o conserva una referencia propia. La base guarda sólo la ruta portable.</div>
        </div>
        <span className="chip">{products.filter((product) => product.mediaRef).length} asignada(s) · {initialWorkspace.meta.libraryCount} opciones</span>
      </div>

      {notice ? <div className="alert-strip" role="status" aria-live="polite"><strong>Imagen</strong><span className="subtle">{notice}</span></div> : null}

      <form className={`${styles.workspace} ${styles.workspaceResponsive}`} onSubmit={save} aria-label="Actualizar imagen de producto">
        <section className={styles.productPicker}>
          <label className="field">
            <span>Buscar producto</span>
            <input value={productQuery} onChange={(event) => setProductQuery(event.target.value)} placeholder="SKU o nombre del producto" autoComplete="off" />
          </label>
          <div className={styles.suggestionList} role="listbox" aria-label="Coincidencias de producto">
            {productMatches.map((product) => (
              <button className={product.id === productId ? styles.selectedSuggestion : styles.suggestion} type="button" key={product.id} onClick={() => selectProduct(product)}>
                <strong>{product.name}</strong><small>{product.sku}</small>
              </button>
            ))}
          </div>
        </section>

        <section className={styles.editor}>
          <div className={styles.modeRow} role="radiogroup" aria-label="Origen de imagen">
            {(["NONE", "LIBRARY", "CUSTOM"] as const).map((value) => (
              <button type="button" key={value} className={mode === value ? styles.modeActive : styles.modeButton} onClick={() => setMode(value)} aria-pressed={mode === value}>
                {value === "NONE" ? "Sin foto" : value === "LIBRARY" ? "Biblioteca" : "Foto propia"}
              </button>
            ))}
          </div>

          {mode === "LIBRARY" ? (
            <>
              <div className={styles.filters}>
                <label className="field"><span>Filtrar imágenes</span><input value={assetQuery} onChange={(event) => setAssetQuery(event.target.value)} placeholder="Papas, leche, botella, limpieza…" /></label>
                <label className="field"><span>Categoría</span><select value={category} onChange={(event) => setCategory(event.target.value)}><option value="all">Todas</option>{categories.map((item) => <option key={item} value={item}>{item.replaceAll("_", " ")}</option>)}</select></label>
              </div>
              <div className={styles.assetGrid}>
                {assetMatches.map((asset) => (
                  <button type="button" key={asset.assetId} className={selectedAssetId === asset.assetId ? styles.assetSelected : styles.assetCard} onClick={() => setSelectedAssetId(asset.assetId)}>
                    <img src={asset.thumbnailPath} alt="" loading="lazy" />
                    <span>{asset.displayName}</span>
                    <small>{asset.category.replaceAll("_", " ")}</small>
                  </button>
                ))}
              </div>
            </>
          ) : null}

          {mode === "CUSTOM" ? (
            <label className="field"><span>URL HTTPS o ruta /product-media/</span><input value={customRef} maxLength={1200} onChange={(event) => setCustomRef(event.target.value)} placeholder="https://… o /product-media/…" /></label>
          ) : null}

          <div className={styles.preview}>
            {preview ? <img src={preview} alt="Vista previa del producto seleccionado" /> : <span>Sin imagen asignada</span>}
            <div><strong>{selected?.name ?? "Selecciona un producto"}</strong><small>{selected?.sku ?? "La selección no modifica inventario ni precio."}</small></div>
          </div>

          <button className="btn btn-primary" type="submit" disabled={!selected || isSaving || initialWorkspace.meta.source !== "canonical_prisma"}>
            {isSaving ? "Guardando…" : "Guardar imagen"}
          </button>
        </section>
      </form>
    </section>
  );
}
