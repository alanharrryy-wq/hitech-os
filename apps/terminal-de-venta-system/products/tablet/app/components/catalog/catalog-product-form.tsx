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
  onSaveAndSell: () => void;
  onSaveAndCreateAnother: () => void;
  onCancelEdit: () => void;
};

export function CatalogProductForm({ form, saving, onChange, onSubmit, onSaveAndSell, onSaveAndCreateAnother, onCancelEdit }: Props) {
  const canSave = Boolean(form.name.trim() && form.sku.trim() && form.price.trim());
  const saveDisabled = saving || !canSave;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className={styles.form} onSubmit={submit}>
      <div className={styles.formHeader}>
        <div>
          <div className={styles.formTitleLine}>
            <strong>{form.id ? "Editar producto" : "Nuevo producto"}</strong>
            <span className={form.id ? styles.editModeBadge : styles.createModeBadge}>{form.id ? "Modo edición" : "Alta nueva"}</span>
          </div>
          <span>{form.id ? `Editando: ${form.name || "producto seleccionado"}. Guarda cambios para aplicar.` : "Alta rápida para que pueda venderse en Tablet."}</span>
        </div>
        {form.id ? <button type="button" className={styles.linkButton} onClick={onCancelEdit}>Nuevo</button> : null}
      </div>

      <label className={styles.field}>
        <span>Nombre</span>
        <input required name="catalog-product-name" data-catalog-field="name" value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} placeholder="Agua natural 600 ml" />
      </label>

      <label className={styles.field}>
        <span>SKU</span>
        <input required name="catalog-product-sku" data-catalog-field="sku" value={form.sku} onChange={(event) => onChange({ ...form, sku: event.target.value })} placeholder="AGUA-600" />
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

      <div className={styles.formActions}>
        <button type="submit" className={styles.saveButton} disabled={saving}>
          {saving ? "Guardando..." : form.id ? "Guardar producto" : "Guardar producto"}
        </button>
        <button type="button" className={styles.secondarySaveButton} disabled={saveDisabled} onClick={onSaveAndSell}>
          Guardar y vender
        </button>
        <button type="button" className={styles.ghostSaveButton} disabled={saveDisabled} onClick={onSaveAndCreateAnother}>
          Guardar y crear otro
        </button>
        <button type="button" className={styles.cancelButton} disabled={saving} onClick={onCancelEdit}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
