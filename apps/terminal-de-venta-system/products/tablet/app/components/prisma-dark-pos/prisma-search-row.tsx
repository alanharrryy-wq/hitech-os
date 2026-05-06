import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaSearchRow() {
  return (
    <section className={styles.searchRow} aria-label="Búsqueda de productos">
      <label className={styles.searchBox}>
        <PrismaIcon name="search" className={styles.searchLeadingIcon} size={22} />
        <input aria-label="Buscar producto" placeholder="Buscar producto por código, nombre o SKU..." type="search" />
        <PrismaIcon name="scan" className={styles.searchTrailingIcon} size={22} />
      </label>

      <button className={styles.scanButton} type="button">
        <PrismaIcon name="scan" size={21} />
        <span>ESCANEAR</span>
      </button>

      <button className={styles.moreButton} type="button" aria-label="Más opciones">
        <PrismaIcon name="more" size={22} />
      </button>
    </section>
  );
}
