"use client";

import { type FormEvent, useMemo, useState } from "react";

type Product = { id: string; sku: string; name: string; mediaRef: string | null; updatedAt: string };
type Workspace = { products: Product[]; meta: { source: "canonical_prisma" | "unavailable"; warning: string | null; generatedAt: string } };

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

export function ProductMediaWorkspace({ initialWorkspace }: { initialWorkspace: Workspace }) {
  const [products, setProducts] = useState(initialWorkspace.products);
  const [productId, setProductId] = useState("");
  const [mediaRef, setMediaRef] = useState("");
  const [notice, setNotice] = useState(initialWorkspace.meta.warning ?? "");
  const [isSaving, setIsSaving] = useState(false);
  const selected = useMemo(() => products.find((product) => product.id === productId) ?? null, [products, productId]);

  function selectProduct(nextId: string) {
    setProductId(nextId);
    const product = products.find((item) => item.id === nextId);
    setMediaRef(product?.mediaRef ?? "");
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setIsSaving(true);
    setNotice("");
    try {
      const data = await readApi<{ product: Product }>(await fetch("/api/backoffice/product-media", {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ productId: selected.id, expectedUpdatedAt: selected.updatedAt, mediaRef: mediaRef.trim() || null })
      }));
      setProducts((current) => current.map((product) => product.id === data.product.id ? data.product : product));
      setMediaRef(data.product.mediaRef ?? "");
      setNotice(data.product.mediaRef ? "Referencia portable guardada. El catálogo PC→Tablet la proyecta con el producto canónico." : "Referencia eliminada. El POS conserva su packshot local de respaldo.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "No fue posible guardar la referencia de imagen.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="card" data-prisma-component="ProductMediaWorkspace" data-prisma-surface="pc.catalog.media">
      <div className="section-head"><div><div className="kicker">referencia portable</div><h2 className="section-title">Imagen de producto</h2><div className="section-copy">Guarda sólo una URL HTTPS o una ruta gestionada; no se almacenan bytes ni credenciales en la base local.</div></div><span className="chip">{products.filter((product) => product.mediaRef).length} asignada(s)</span></div>
      {notice ? <div className="alert-strip" role="status" aria-live="polite"><strong>Imagen</strong><span className="subtle">{notice}</span></div> : null}
      <form className="inline-list" onSubmit={save} aria-label="Actualizar referencia de imagen de producto">
        <label className="field"><span>Producto</span><select required value={productId} onChange={(event) => selectProduct(event.target.value)}><option value="">Seleccionar SKU</option>{products.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.name}</option>)}</select></label>
        <label className="field"><span>Referencia</span><input value={mediaRef} maxLength={1200} onChange={(event) => setMediaRef(event.target.value)} placeholder="https://… o /product-media/…" /></label>
        <button className="btn btn-primary" type="submit" disabled={!selected || isSaving || initialWorkspace.meta.source !== "canonical_prisma"}>{isSaving ? "Guardando…" : "Guardar imagen"}</button>
      </form>
    </section>
  );
}
