import { navItems } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaSidebar() {
  return (
    <aside className={styles.sidebar} aria-label="Navegación principal">
      <div className={styles.brandBlock}>
        <PrismaMark />
        <div className={styles.wordmark}>PRISMA</div>
        <div className={styles.brandSubtitle}>SISTEMA DE GESTIÓN INTELIGENTE</div>
      </div>

      <nav className={styles.navList}>
        {navItems.map((item) => (
          <a key={item.label} className={item.active ? styles.navItemActive : styles.navItem} href="#">
            <PrismaIcon name={item.icon} size={19} />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <div className={styles.terminalCard}>
        <div className={styles.terminalIconWrap}>
          <PrismaIcon name="terminal" size={19} />
          <span className={styles.onlineDot} />
        </div>
        <div className={styles.terminalText}>
          <strong>Terminal 01</strong>
          <span>En línea</span>
        </div>
        <PrismaIcon name="chevron-down" className={styles.terminalChevron} size={16} />
      </div>
    </aside>
  );
}

function PrismaMark() {
  return (
    <svg className={styles.prismaMark} viewBox="0 0 80 72" role="img" aria-label="PRISMA">
      <path className={styles.prismaMarkBack} d="M40 5 72 24 40 67 8 24 40 5Z" />
      <path className={styles.prismaMarkFacet} d="M40 5v62L8 24 40 5Z" />
      <path className={styles.prismaMarkFacetTwo} d="M40 5v62l32-43L40 5Z" />
      <path className={styles.prismaMarkLine} d="M8 24h64M22 24l18 43 18-43M40 5 22 24M40 5l18 19" />
    </svg>
  );
}
