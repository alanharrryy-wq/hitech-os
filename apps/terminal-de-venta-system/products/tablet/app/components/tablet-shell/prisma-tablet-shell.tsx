import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { TABLET_NAV_ITEMS, isTabletNavActive } from "./tablet-nav";
import styles from "./prisma-tablet-shell.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

export function TabletShellStatusPill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={[styles.statusPill, styles[`status_${tone}`]].join(" ")}>{children}</span>;
}

export function PrismaTabletShellUnified({
  currentPath,
  title,
  subtitle,
  kicker = "Tablet vende sola",
  status,
  actions,
  children
}: {
  currentPath: string;
  title: string;
  subtitle: string;
  kicker?: string;
  status?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className={styles.shell}>
      <a className={styles.skipLink} href="#contenido-principal">Saltar al contenido</a>
      <aside className={styles.sidebar} aria-label="Navegación principal de Tablet">
        <a className={styles.brand} href="/pos" aria-label="Ir a vender en PRISMA Tablet">
          <span className={styles.brandMark}>P</span>
          <span className={styles.brandText}>
            <strong>PRISMA</strong>
            <small>Tablet</small>
          </span>
        </a>

        <nav className={styles.navList} aria-label="Módulos operativos">
          {TABLET_NAV_ITEMS.map((item) => {
            const active = isTabletNavActive(currentPath, item.href);
            return (
              <a
                key={item.href}
                className={active ? styles.navActive : styles.navItem}
                href={item.href}
                aria-current={active ? "page" : undefined}
                title={item.description}
              >
                <PrismaIcon name={item.icon} size={19} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>

        <div className={styles.terminalCard} aria-label="Estado de terminal">
          <span className={styles.terminalIcon}>
            <PrismaIcon name="terminal" size={18} />
          </span>
          <span>
            <strong>Terminal local</strong>
            <small>Venta autónoma</small>
          </span>
        </div>
      </aside>

      <main id="contenido-principal" className={styles.main}>
        <header className={styles.header}>
          <div className={styles.titleGroup}>
            <span className={styles.kicker}>{kicker}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          {status ? <div className={styles.statusArea}>{status}</div> : null}
        </header>
        {actions ? <section className={styles.actionBand} aria-label="Acciones de pantalla">{actions}</section> : null}
        <div className={styles.content}>{children}</div>
      </main>
    </div>
  );
}
