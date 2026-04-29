import type { CatalogProductFormState } from "@/lib/catalog/product-form-state";
import { CatalogProductForm } from "./catalog-product-form";
import styles from "./catalog.module.css";

type Props = {
  form: CatalogProductFormState;
  saving: boolean;
  onChange: (next: CatalogProductFormState) => void;
  onSubmit: () => void;
  onCancelEdit: () => void;
};

export function CatalogProductDrawer(props: Props) {
  return (
    <aside className={styles.drawer} aria-label="Alta rápida de producto">
      <CatalogProductForm {...props} />
      <div className={styles.drawerNote}>
        <strong>Proveedor completo va en PC</strong>
        <span>Tablet solo crea producto vendible y existencia local. Compras, recepción y proveedor formal viven en Backoffice.</span>
      </div>
    </aside>
  );
}
