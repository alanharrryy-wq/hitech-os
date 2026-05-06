import type { CatalogProduct } from "@/lib/catalog/product-form-state";
import { formatMoney } from "@/lib/catalog/product-form-state";
import styles from "./catalog.module.css";

type Props = {
  products: CatalogProduct[];
  selectedId?: string;
  onEdit: (product: CatalogProduct) => void;
};

export function CatalogProductTable({ products, selectedId, onEdit }: Props) {
  if (!products.length) {
    return (
      <div className={styles.emptyState}>
        <strong>No hay productos para mostrar</strong>
        <span>Busca otro texto o crea un producto nuevo desde el panel derecho.</span>
      </div>
    );
  }

  return (
    <div className={styles.tableWrap}>
      <table className={styles.productTable}>
        <thead>
          <tr>
            <th>Producto</th>
            <th>SKU</th>
            <th>Código</th>
            <th>Precio</th>
            <th>Existencias</th>
            <th>Estado</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id} className={selectedId === product.id ? styles.selectedRow : undefined}>
              <td>
                <strong>{product.name}</strong>
                <small>{product.category || "General"}</small>
              </td>
              <td>{product.sku}</td>
              <td>{product.barcode || product.barcodes?.[0] || "Sin código"}</td>
              <td>{formatMoney(product.priceCents)}</td>
              <td>{product.stockOnHand}</td>
              <td><span className={product.isActive ? styles.badgeOk : styles.badgeMuted}>{product.isActive ? "Activo" : "Inactivo"}</span></td>
              <td><button type="button" className={styles.tableAction} onClick={() => onEdit(product)}>Editar</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
