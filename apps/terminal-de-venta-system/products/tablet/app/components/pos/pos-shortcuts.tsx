import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import styles from "./pos.module.css";

export function PosShortcuts() {
  return (
    <section className={styles.shortcuts} aria-label="Atajos de caja">
      <a href="/catalog"><PrismaIcon name="tag" size={18} /><span>Catálogo</span></a>
      <a href="/sales/today"><PrismaIcon name="receipt" size={18} /><span>Ventas de hoy</span></a>
      <a href="/settings/export"><PrismaIcon name="save" size={18} /><span>Exportar</span></a>
    </section>
  );
}
