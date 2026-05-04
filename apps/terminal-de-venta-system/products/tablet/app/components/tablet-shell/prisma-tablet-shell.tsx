import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { TabletRuntimeStatusStrip } from "@components/tablet-runtime/tablet-runtime-status-strip";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { getTabletFlowCopy, getTabletFlowStage, getVisibleTabletNavItems, isTabletNavActive } from "./tablet-nav";
import styles from "./prisma-tablet-shell.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

export function TabletShellStatusPill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={[styles.statusPill, styles[`status_${tone}`]].join(" ")} data-prisma-component="StatusPill">{children}</span>;
}

export function PrismaTabletShellUnified({
  currentPath,
  title,
  subtitle,
  kicker = "Tablet vende sola",
  status,
  actions,
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT,
  visualSurface,
  visualPreset,
  children
}: {
  currentPath: string;
  title: string;
  subtitle: string;
  kicker?: string;
  status?: ReactNode;
  actions?: ReactNode;
  runtimeSnapshot?: TabletRuntimeSnapshot;
  visualSurface?: string;
  visualPreset?: string;
  children: ReactNode;
}) {
  const flowStage = getTabletFlowStage(currentPath);
  const flowCopy = getTabletFlowCopy(flowStage, runtimeSnapshot);
  const visibleNavItems = getVisibleTabletNavItems(currentPath, runtimeSnapshot);

  return (
    <div
      className={styles.shell}
      data-prisma-component="AppShell"
      data-prisma-product="tablet"
      data-prisma-flow-stage={flowStage}
      data-prisma-visual-surface={visualSurface}
      data-prisma-visual-preset={visualPreset}
      data-prisma-preset={visualPreset}
    >
      <a className={styles.skipLink} href="#contenido-principal">Saltar al contenido</a>
      <aside className={styles.sidebar} aria-label="Navegacion principal de Tablet" data-prisma-component="Sidebar">
        <a className={styles.brand} href="/" aria-label="Ir al inicio operativo de PRISMA Tablet" data-prisma-component="BrandBlock">
          <span className={styles.brandMark} aria-hidden="true">
            <span className={styles.prismaShard} />
          </span>
          <span className={styles.brandText}>
            <strong>PRISMA</strong>
            <small>Sistema de gestion inteligente</small>
          </span>
        </a>

        <nav className={styles.navList} aria-label="Modulos operativos" data-prisma-component="GuidedSidebarNav" data-prisma-visible-count={visibleNavItems.length}>
          <div className={styles.navFlowHint} data-prisma-component="GuidedSidebarHint">
            <span>{flowCopy.label}</span>
            <small>{flowCopy.helper}</small>
          </div>
          {visibleNavItems.map((item) => {
            const active = isTabletNavActive(currentPath, item.href);
            return (
              <a
                key={item.href}
                className={active ? styles.navActive : item.primary ? styles.navPrimary : styles.navItem}
                href={item.href}
                aria-current={active ? "page" : undefined}
                title={item.description}
                data-prisma-component="NavItem"
                data-prisma-flow-nav="true"
                data-active={active ? "true" : undefined}
                data-primary={item.primary ? "true" : undefined}
                data-group={item.group}
              >
                <PrismaIcon name={item.icon} size={19} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>

        <div className={styles.terminalCard} aria-label="Estado de terminal" data-prisma-component="TerminalStatusCard">
          <span className={styles.terminalIcon}>
            <PrismaIcon name="terminal" size={18} />
          </span>
          <span>
            <strong>{runtimeSnapshot.identity.terminalName}</strong>
            <small>{runtimeSnapshot.localSalesAllowed ? "Venta autonoma" : "Revisar venta"}</small>
          </span>
        </div>
      </aside>

      <main id="contenido-principal" className={styles.main}>
        <header className={styles.header} data-prisma-component="TopBar">
          <div className={styles.titleGroup}>
            <span className={styles.kicker}>{kicker}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className={styles.headerControls} data-prisma-component="UserMenu">
            <a className={styles.headerIconButton} href="/shift" aria-label="Ver turno">
              <PrismaIcon name="terminal" size={20} />
            </a>
            <a className={styles.headerIconButton} href="/sync" aria-label="Ver pendientes">
              <PrismaIcon name="bell" size={20} />
              <span>{runtimeSnapshot.connection.pendingEvents + runtimeSnapshot.connection.failedEvents + runtimeSnapshot.connection.conflictEvents}</span>
            </a>
            {status ? <div className={styles.statusArea}>{status}</div> : null}
          </div>
        </header>
        <TabletRuntimeStatusStrip snapshot={runtimeSnapshot} />
        {actions ? <section className={styles.actionBand} aria-label="Acciones de pantalla" data-prisma-component="SecondaryActionCard">{actions}</section> : null}
        <div className={styles.content}>{children}</div>
      </main>
    </div>
  );
}
