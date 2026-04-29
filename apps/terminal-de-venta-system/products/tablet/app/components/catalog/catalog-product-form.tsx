import type { FormEvent } from "react";
import type { CatalogProductFormState } from "@/lib/catalog/product-form-state";
import { CatalogBarcodeField } from "./catalog-barcode-field";
import { CatalogStockField } from "./catalog-stock-field";
import styles from "./catalog.module.css";

type Props = {
  form: CatalogProductFormState;
  saving: boolean;
  onChange: (next: CatalogProductFormState) => void;
  onSubmit: () => void;
  onCancelEdit: () => void;
};

export function CatalogProductForm({ form, saving, onChange, onSubmit, onCancelEdit }: Props) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className={styles.form} onSubmit={submit}>
      <div className={styles.formHeader}>
        <div>
          <strong>{form.id ? "Editar producto" : "Nuevo producto"}</strong>
          <span>{form.id ? "Ajusta datos básicos para venta local." : "Alta rápida para que pueda venderse en Tablet."}</span>
        </div>
        {form.id ? <button type="button" className={styles.linkButton} onClick={onCancelEdit}>Nuevo</button> : null}
      </div>

      <label className={styles.field}>
        <span>Nombre</span>
        <input required value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} placeholder="Agua natural 600 ml" />
      </label>

      <label className={styles.field}>
        <span>SKU</span>
        <input required value={form.sku} onChange={(event) => onChange({ ...form, sku: event.target.value })} placeholder="AGUA-600" />
      </label>

      <CatalogBarcodeField value={form.barcode} productId={form.id} onChange={(barcode) => onChange({ ...form, barcode })} />

      <label className={styles.field}>
        <span>Categoría</span>
        <input value={form.category} onChange={(event) => onChange({ ...form, category: event.target.value })} placeholder="Bebidas" />
      </label>

      <div className={styles.twoCols}>
        <label className={styles.field}>
          <span>Precio venta</span>
          <input required value={form.price} onChange={(event) => onChange({ ...form, price: event.target.value })} type="number" min="0" step="0.01" placeholder="18.00" />
        </label>
        <label className={styles.field}>
          <span>Costo</span>
          <input value={form.cost} onChange={(event) => onChange({ ...form, cost: event.target.value })} type="number" min="0" step="0.01" placeholder="10.00" />
        </label>
      </div>

      <CatalogStockField value={form.stockOnHand} onChange={(stockOnHand) => onChange({ ...form, stockOnHand })} />

      <label className={styles.toggleField}>
        <input type="checkbox" checked={form.isActive} onChange={(event) => onChange({ ...form, isActive: event.target.checked })} />
        <span>Producto activo para venta</span>
      </label>

      <button type="submit" className={styles.saveButton} disabled={saving}>
        {saving ? "Guardando..." : form.id ? "Guardar cambios" : "Crear producto"}
      </button>
    </form>
  );
}
