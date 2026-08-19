"use client";

import { type FormEvent, useState } from "react";

type Product = { id: string; sku: string; name: string; isActive: boolean };
type Variant = {
  id: string;
  productId: string;
  productSku: string;
  productName: string;
  variantProductId: string;
  variantSku: string;
  variantName: string;
  label: string;
  attributes: Record<string, string>;
  status: "ACTIVE" | "INACTIVE";
  version: number;
};

type Workspace = {
  variants: Variant[];
  products: Product[];
  meta: { source: "canonical_prisma" | "unavailable"; warning: string | null; generatedAt: string };
};

function idempotencyKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  return `pc-product-variant-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

function attributesLabel(attributes: Record<string, string>) {
  const values = Object.entries(attributes).map(([key, value]) => `${key}: ${value}`);
  return values.length ? values.join(" · ") : "Sin atributos adicionales";
}

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

export function ProductVariantWorkspace({ initialWorkspace }: { initialWorkspace: Workspace }) {
  const [variants, setVariants] = useState(initialWorkspace.variants);
  const [notice, setNotice] = useState(initialWorkspace.meta.warning ?? "");
  const [isCreating, setIsCreating] = useState(false);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [form, setForm] = useState({ productId: "", variantProductId: "", label: "", color: "", size: "", sortOrder: "0" });

  async function createVariant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setNotice("");
    try {
      const data = await readApi<{ variant: Variant; replayed: boolean }>(await fetch("/api/backoffice/product-variants", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          productId: form.productId,
          variantProductId: form.variantProductId,
          label: form.label,
          attributes: { ...(form.color.trim() ? { color: form.color.trim() } : {}), ...(form.size.trim() ? { size: form.size.trim() } : {}) },
          sortOrder: Number(form.sortOrder),
          idempotencyKey: idempotencyKey()
        })
      }));
      setVariants((current) => [data.variant, ...current.filter((variant) => variant.id !== data.variant.id)]);
      setForm({ productId: "", variantProductId: "", label: "", color: "", size: "", sortOrder: "0" });
      setNotice(data.replayed ? "La solicitud ya existía y recuperamos la variante." : "Variante creada correctamente.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "No fue posible crear la variante.");
    } finally {
      setIsCreating(false);
    }
  }

  async function deactivate(variant: Variant) {
    setPendingId(variant.id);
    setNotice("");
    try {
      const data = await readApi<{ variant: Variant }>(await fetch(`/api/backoffice/product-variants/${encodeURIComponent(variant.id)}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ expectedVersion: variant.version, status: "INACTIVE" })
      }));
      setVariants((current) => current.map((item) => item.id === data.variant.id ? data.variant : item));
      setNotice("Variante desactivada. Los productos y su historial se conservaron sin cambios.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "No fue posible desactivar la variante.");
    } finally {
      setPendingId(null);
    }
  }

  return (
    <section className="card" data-prisma-component="ProductVariantWorkspace" data-prisma-surface="pc.catalog.variants">
      <div className="section-head">
        <div><div className="kicker">variantes</div><h2 className="section-title">Variantes vendibles</h2><div className="section-copy">Relaciona productos existentes por color, talla u otra presentación sin duplicar su información comercial.</div></div>
        <span className="chip">{variants.filter((variant) => variant.status === "ACTIVE").length} activa(s)</span>
      </div>

      {notice ? <div className="alert-strip" role="status" aria-live="polite"><strong>Variantes</strong><span className="subtle">{notice}</span></div> : null}

      <form className="inline-list" onSubmit={createVariant} aria-label="Crear variante de producto">
        <label className="field"><span>Producto base</span><select required value={form.productId} onChange={(event) => setForm((current) => ({ ...current, productId: event.target.value }))}><option value="">Seleccionar SKU</option>{initialWorkspace.products.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.name}</option>)}</select></label>
        <label className="field"><span>Producto variante</span><select required value={form.variantProductId} onChange={(event) => setForm((current) => ({ ...current, variantProductId: event.target.value }))}><option value="">Seleccionar SKU</option>{initialWorkspace.products.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.name}</option>)}</select></label>
        <label className="field"><span>Etiqueta</span><input required minLength={2} maxLength={140} value={form.label} onChange={(event) => setForm((current) => ({ ...current, label: event.target.value }))} placeholder="Ej. Azul · M" /></label>
        <label className="field"><span>Color</span><input maxLength={80} value={form.color} onChange={(event) => setForm((current) => ({ ...current, color: event.target.value }))} /></label>
        <label className="field"><span>Talla</span><input maxLength={80} value={form.size} onChange={(event) => setForm((current) => ({ ...current, size: event.target.value }))} /></label>
        <button className="btn btn-primary" type="submit" disabled={isCreating || initialWorkspace.meta.source !== "canonical_prisma"}>{isCreating ? "Creando…" : "Vincular variante"}</button>
      </form>

      {!variants.length ? <p className="subtle">Aún no hay variantes configuradas.</p> : <div className="list" aria-label="Variantes configuradas">
        {variants.map((variant) => <article className="list-item" key={variant.id} data-product-variant-status={variant.status}>
          <div><strong>{variant.productSku} · {variant.productName}</strong><div>{variant.label} → {variant.variantSku} · {variant.variantName}</div><span className="subtle">{attributesLabel(variant.attributes)} · {variant.status === "ACTIVE" ? "Activa" : "Inactiva"}</span></div>
          {variant.status === "ACTIVE" ? <button className="btn" type="button" disabled={pendingId === variant.id} onClick={() => void deactivate(variant)}>{pendingId === variant.id ? "Guardando…" : "Desactivar"}</button> : <span className="chip">Historial conservado</span>}
        </article>)}
      </div>}
    </section>
  );
}
