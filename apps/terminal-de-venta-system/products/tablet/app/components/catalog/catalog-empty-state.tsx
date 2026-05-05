import styles from "./catalog.module.css";

export function CatalogEmptyState() {
  return (
    <div className={styles.emptyState}>
      <strong>Catálogo listo para operar</strong>
      <span>Busca productos existentes o usa “Nuevo producto” para dar de alta lo básico.</span>
    </div>
  );
}
