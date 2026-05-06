import { categories } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaCategoryRail() {
  return (
    <section className={styles.categoryRail} aria-label="Categorías">
      {categories.map((category) => (
        <button key={category.label} className={category.active ? styles.categoryActive : styles.categoryItem} type="button">
          <span className={styles.categoryCircle}>
            <PrismaIcon name={category.icon} size={22} />
          </span>
          <span className={styles.categoryLabel}>{category.label}</span>
        </button>
      ))}

      <button className={styles.categoryNext} type="button" aria-label="Ver más categorías">
        <span className={styles.categoryCircle}>
          <PrismaIcon name="arrow-right" size={21} />
        </span>
      </button>
    </section>
  );
}
