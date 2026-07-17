"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { catalogVisibleError } from "@/lib/catalog/product-visible-errors";
import type { CatalogProduct, CatalogProductFormState } from "@/lib/catalog/product-form-state";
import { catalogRequest, emptyProductForm, formToPayload, productToForm } from "@/lib/catalog/product-form-state";
import { CatalogProductTable } from "./catalog-product-table";
import { CatalogProductDrawer } from "./catalog-product-drawer";
import styles from "./catalog.module.css";

export function ProductCatalogWorkspace() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState("");
  const [includeInactive, setIncludeInactive] = useState(true);
  const [products, setProducts] = useState<CatalogProduct[]>([]);
  const [form, setForm] = useState<CatalogProductFormState>({ ...emptyProductForm });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState("");

  const drawerDockRef = useRef<HTMLDivElement | null>(null);

  function beginEditProduct(product: CatalogProduct) {
    setForm(productToForm(product));
    setNotice(`Editando ${product.name}. Revisa el panel derecho y guarda cambios.`);
    setError(null);

    window.requestAnimationFrame(() => {
      drawerDockRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
      const firstInput = drawerDockRef.current?.querySelector<HTMLInputElement>("[data-catalog-field='name']");
      firstInput?.focus({ preventScroll: true });
      firstInput?.select();
    });
  }

  function beginNewProduct() {
    setForm({ ...emptyProductForm });
    setNotice("Listo para registrar producto nuevo. Completa nombre, precio, SKU y existencia.");
    setError(null);

    window.requestAnimationFrame(() => {
      drawerDockRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
      const firstInput = drawerDockRef.current?.querySelector<HTMLInputElement>("[data-catalog-field='name']");
      firstInput?.focus({ preventScroll: true });
      firstInput?.select();
    });
  }

  const activeCount = useMemo(() => products.filter((product) => product.isActive).length, [products]);

  async function loadProducts(nextQuery = query) {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ q: nextQuery, limit: "50", includeInactive: includeInactive ? "true" : "false" });
      const response = await catalogRequest<{ products: CatalogProduct[]; count: number }>(`/api/pos/products/search?${params.toString()}`);
      setProducts(response.data.products);
    } catch (caught) {
      setError(caught);
    } finally {
      setLoading(false);
    }
  }

  async function saveProduct(nextAction: "stay" | "sell" | "another" = "stay") {
    setSaving(true);
    setError(null);
    setNotice("");
    try {
      const endpoint = form.id ? "/api/pos/products/update" : "/api/pos/products/create";
      const response = await catalogRequest<{ product: CatalogProduct }>(endpoint, {
        method: "POST",
        body: JSON.stringify(formToPayload(form))
      });
      setNotice(form.id ? "Producto actualizado." : "Producto creado y listo para venta.");
      if (nextAction === "another") {
        setForm({ ...emptyProductForm });
      } else {
        setForm(productToForm(response.data.product));
      }
      await loadProducts(query);
      if (nextAction === "sell") {
        window.location.href = "/pos";
      }
    } catch (caught) {
      setError(caught);
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadProducts("");
  }, [includeInactive]);

  useEffect(() => {
    const sku = searchParams.get("sku")?.trim() || searchParams.get("code")?.trim() || "";
    const wantsNewProduct = searchParams.get("new") === "1";
    if (wantsNewProduct && !sku) {
      beginNewProduct();
      return;
    }
    if (!sku) return;
    setForm((current) => {
      if (current.id || current.sku || current.barcode) return current;
      return { ...current, sku, barcode: sku };
    });
    setQuery(sku);
    setNotice("Código precargado desde POS. Completa nombre, precio y existencia para venderlo.");
  }, [searchParams]);

  return (
    <PrismaTabletShellUnified
      currentPath="/catalog"
      title="Catálogo"
      subtitle="Consulta, crea y edita productos básicos para vender en Tablet sin pedirle permiso a PC."
      status={<TabletShellStatusPill tone={error ? "danger" : "ok"}>{error ? "Revisar catálogo" : `${activeCount} activos`}</TabletShellStatusPill>}
    >
      <div className={styles.catalogLayout}>
        <section className={styles.catalogMain} aria-label="Catálogo de productos">
          <div className={styles.toolbar}>
            <div>
              <span className={styles.kicker}>Operación local</span>
              <h2>Productos vendibles</h2>
            </div>
            <button className={styles.saveButton} type="button" onClick={beginNewProduct} aria-controls="catalog-product-form">
              Nuevo producto
            </button>
            <div className={styles.searchBox}>
              <input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void loadProducts(query); }} placeholder="Buscar por nombre, SKU o código" />
              <button type="button" onClick={() => void loadProducts(query)} disabled={loading}>{loading ? "Buscando..." : "Buscar"}</button>
            </div>
            <label className={styles.compactCheck}>
              <input type="checkbox" checked={includeInactive} onChange={(event) => setIncludeInactive(event.target.checked)} />
              <span>Incluir inactivos</span>
            </label>
          </div>

          {notice ? <div className={styles.notice} role="status">{notice}</div> : null}
          {error ? <div className={styles.errorBox} role="alert">{catalogVisibleError(error)}</div> : null}

          <CatalogProductTable products={products} selectedId={form.id} onEdit={beginEditProduct} />
        </section>

        <div ref={drawerDockRef} id="catalog-product-form" className={styles.drawerDock} data-editing={form.id ? "true" : "false"}>
          <CatalogProductDrawer
            form={form}
            saving={saving}
            onChange={setForm}
            onSubmit={() => void saveProduct("stay")}
            onSaveAndSell={() => void saveProduct("sell")}
            onSaveAndCreateAnother={() => void saveProduct("another")}
            onCancelEdit={() => { setForm({ ...emptyProductForm }); setNotice(""); setError(null); }}
          />
        </div>
      </div>
    </PrismaTabletShellUnified>
  );
}

/** @deprecated Use ProductCatalogWorkspace as the canonical route owner. */
export const CatalogScreen = ProductCatalogWorkspace;
