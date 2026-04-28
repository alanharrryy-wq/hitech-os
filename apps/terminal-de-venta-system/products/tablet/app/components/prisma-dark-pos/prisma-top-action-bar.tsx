import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaTopActionBar() {
  return (
    <div className={styles.topActions} aria-label="Acciones de sesión">
      <button className={styles.iconButton} type="button" aria-label="Cambiar tema">
        <PrismaIcon name="sun" size={20} />
      </button>
      <button className={styles.iconButtonBadge} type="button" aria-label="Notificaciones">
        <PrismaIcon name="bell" size={20} />
        <span>3</span>
      </button>
      <button className={styles.adminChip} type="button">
        <span className={styles.adminAvatar}>AR</span>
        <span className={styles.adminMeta}>
          <strong>Administrador</strong>
          <small>Sucursal Centro</small>
        </span>
        <PrismaIcon name="chevron-down" size={15} />
      </button>
    </div>
  );
}
