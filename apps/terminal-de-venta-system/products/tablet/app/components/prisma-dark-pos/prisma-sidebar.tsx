import { navItems } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

export function PrismaSidebar() {
  return (
    <aside className={styles.sidebar} aria-label="Navegación principal"
      data-surface="tablet"
      data-screen="pos"
      data-zone="pos"
      data-panel="prisma-sidebar"
      data-target="prisma-sidebar-navegaci-n-principal-7"
      data-kind="text"
      data-role="copy"
    >
      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-div-1" data-kind="panel" data-role="container" className={styles.brandBlock}>
        <PrismaMark />
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-div-2" data-kind="panel" data-role="container" className={styles.wordmark}>PRISMA</div>
        <div className={styles.brandSubtitle}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-sidebar"
          data-target="prisma-sidebar-text-11"
          data-kind="text"
          data-role="copy"
        >SISTEMA DE GESTIÓN INTELIGENTE</div>
      </div>

      <nav className={styles.navList}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-sidebar"
        data-target="prisma-sidebar-table-14"
        data-kind="table"
        data-role="data-display"
      >
        {navItems.map((item) => (
          <a key={item.label} className={item.active ? styles.navItemActive : styles.navItem} href="#"
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="prisma-sidebar"
            data-target="prisma-sidebar-cart-16"
            data-kind="cart"
            data-role="revenue-core"
          >
            <PrismaIcon name={item.icon} size={19} />
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-span-3" data-kind="text" data-role="text">{item.label}</span>
          </a>
        ))}
      </nav>

      <div className={styles.terminalCard}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-sidebar"
        data-target="prisma-sidebar-panel-23"
        data-kind="panel"
        data-role="revenue-core"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-div-4" data-kind="panel" data-role="container" className={styles.terminalIconWrap}>
          <PrismaIcon name="terminal" size={19} />
          <span className={styles.onlineDot}
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="prisma-sidebar"
            data-target="prisma-sidebar-cart-26"
            data-kind="cart"
            data-role="revenue-core"
          />
        </div>
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-div-5" data-kind="panel" data-role="container" className={styles.terminalText}>
          <strong
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="prisma-sidebar"
            data-target="prisma-sidebar-element-29"
            data-kind="element"
            data-role="revenue-core"
          >Terminal 01</strong>
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="prisma_sidebar" data-target="prisma-sidebar-span-6" data-kind="text" data-role="text">En línea</span>
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
