import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { TabletRuntimeStatusStrip } from "@components/tablet-runtime/tablet-runtime-status-strip";
import { PrismaDarkSelector } from "@components/ui/prisma-dark-selector";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import {
  TABLET_NAV_GROUP_LABELS,
  getTabletFlowCopy,
  getTabletFlowStage,
  getTabletPendingCount,
  getVisibleTabletNavItems,
  isTabletNavActive,
  type TabletNavGroup
} from "./tablet-nav";
import styles from "./prisma-tablet-shell.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

export function TabletShellStatusPill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={[styles.statusPill, styles[`status_${tone}`]].join(" ")} data-prisma-component="StatusPill">{children}</span>;
}

const NAV_GROUP_ORDER: TabletNavGroup[] = ["operacion", "consulta", "soporte"];

function getScreenZone(currentPath: string) {
  if (currentPath === "/") return "tablet-home-root";
  if (currentPath === "/sales/today" || currentPath.startsWith("/sales/today/") || currentPath === "/sales") return "tablet-sales-today-root";
  if (currentPath === "/shift") return "tablet-shift-root";
  if (currentPath === "/sync" || currentPath === "/events/outbox") return "tablet-sync-root";
  if (currentPath === "/offline" || currentPath === "/settings/export") return "tablet-offline-export-root";
  if (currentPath === "/returns" || currentPath.includes("/return")) return "tablet-returns-root";
  if (currentPath === "/catalog" || currentPath === "/stock" || currentPath === "/existencias" || currentPath === "/inventory" || currentPath === "/inventory/low-stock") return "tablet-catalog-stock-assist-root";
  return undefined;
}

function getScreenQa(currentPath: string) {
  if (currentPath === "/sync" || currentPath === "/events/outbox") return "tablet-qa-sync";
  if (currentPath === "/catalog" || currentPath === "/stock" || currentPath === "/existencias" || currentPath === "/inventory" || currentPath === "/inventory/low-stock") return "tablet-qa-product-card";
  return undefined;
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
  const pendingCount = getTabletPendingCount(runtimeSnapshot);
  const screenZone = getScreenZone(currentPath);
  const screenQa = getScreenQa(currentPath);
  const groupedNavItems = NAV_GROUP_ORDER.map((group) => ({
    group,
    label: TABLET_NAV_GROUP_LABELS[group],
    items: visibleNavItems.filter((item) => item.group === group)
  })).filter((group) => group.items.length > 0);

  return (
    <>
      <input id="prisma-tablet-sidebar-toggle" className={styles.sidebarToggleInput} type="checkbox" aria-label="Contraer o expandir navegación de PRISMA Tablet" />
      <div
        className={styles.shell}
        data-prisma-component="AppShell"
        data-prisma-product="tablet"
        data-prisma-flow-stage={flowStage}
        data-prisma-visual-surface={visualSurface}
        data-prisma-visual-preset={visualPreset}
        data-prisma-preset={visualPreset}
        data-prisma-vos-runtime="00E"
        data-prisma-motion="ambient"
        data-prisma-cloudglass="background-static-all-tablet"
        data-prisma-background="tablet-background-active-fixed"
      >
        <a className={styles.skipLink} href="#contenido-principal">Saltar al contenido</a>
        <aside className={styles.sidebar} aria-label="Navegación principal de Tablet" data-prisma-component="Sidebar" data-prisma-role="operational-summary">
          <label className={styles.brand} htmlFor="prisma-tablet-sidebar-toggle" title="Contraer o expandir navegación" data-prisma-component="BrandCollapseToggle">
            <span className={styles.brandMark} aria-hidden="true">
              <img className={styles.brandImage} src="/prisma/logo-prisma-primary.png" alt="" />
              <span className={styles.prismaShard} />
            </span>
            <span className={styles.brandText}>
              <strong>PRISMA</strong>
              <small>Sistema de gestión inteligente</small>
            </span>
          </label>

          <nav className={styles.navList} aria-label="Módulos operativos" data-prisma-component="GuidedSidebarNav" data-prisma-visible-count={visibleNavItems.length}>
            <div className={styles.navFlowHint} data-prisma-component="GuidedSidebarHint">
              <span>{flowCopy.label}</span>
              <small>{flowCopy.helper}</small>
            </div>
            {groupedNavItems.map((group) => {
              const groupHasActiveItem = group.items.some((item) => isTabletNavActive(currentPath, item.href));
              const groupHasAttention = group.group === "soporte" && pendingCount > 0;

              return (
                <details
                  className={styles.navGroup}
                  key={group.group}
                  open
                  aria-label={group.label}
                  data-group={group.group}
                  data-active={groupHasActiveItem ? "true" : undefined}
                  data-attention={groupHasAttention ? "true" : undefined}
                  data-prisma-component="CollapsibleNavGroup"
                >
                  <summary className={styles.navGroupSummary} aria-label={`Mostrar u ocultar ${group.label}`}>
                    <span className={styles.navGroupTitle}>{group.label}</span>
                    <span className={styles.navGroupMeta}>{group.items.length}</span>
                    <span className={styles.navGroupChevron} aria-hidden="true">⌄</span>
                  </summary>
                  <div className={styles.navGroupItems}>
                    {group.items.map((item) => {
                      const active = isTabletNavActive(currentPath, item.href);
                      const showPendingBadge = item.href === "/sync" && pendingCount > 0;
                      return (
                        <a
                          key={item.href}
                          className={active ? styles.navActive : item.primary ? styles.navPrimary : styles.navItem}
                          href={item.href}
                          aria-current={active ? "page" : undefined}
                          aria-label={`${item.label}. ${item.description}`}
                          title={item.description}
                          data-prisma-component="NavItem"
                          data-prisma-flow-nav="true"
                          data-active={active ? "true" : undefined}
                          data-primary={item.primary ? "true" : undefined}
                          data-group={item.group}
                          data-attention={showPendingBadge ? "true" : undefined}
                          data-prisma-role={item.primary ? "primary-action" : "secondary-action"}
                          data-prisma-priority={item.primary ? "primary" : active ? "secondary" : "support"}
                          data-prisma-state={active ? "selected" : showPendingBadge ? "sync_pending" : undefined}
                          data-prisma-motion="press-feedback"
                        >
                          <PrismaIcon name={item.icon} size={19} />
                          <span className={styles.navText}>
                            <span className={styles.navLabel}>{item.label}</span>
                            {item.primary ? <small>{item.description}</small> : null}
                          </span>
                          {showPendingBadge ? <span className={styles.navBadge} aria-label={`${pendingCount} pendientes`}>{pendingCount}</span> : null}
                        </a>
                      );
                    })}
                  </div>
                </details>
              );
            })}
          </nav>

          <div className={styles.terminalCard} aria-label="Estado de terminal" data-prisma-component="TerminalStatusCard">
            <span className={styles.terminalIcon}>
              <PrismaIcon name="terminal" size={18} />
            </span>
            <span>
              <strong>{runtimeSnapshot.identity.terminalName}</strong>
              <small>{runtimeSnapshot.localSalesAllowed ? "Venta autónoma" : "Revisar venta"}</small>
            </span>
          </div>
        </aside>

        <main id="contenido-principal" className={styles.main}>
          <header className={styles.header} data-prisma-component="TopCommandBar" data-prisma-role="operational-summary">
            <div className={styles.titleGroup}>
              <span className={styles.kicker}>{kicker}</span>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
            <TabletRuntimeStatusStrip snapshot={runtimeSnapshot} variant="compact" />
            <div className={styles.headerControls} data-prisma-component="UserMenu" data-prisma-role="status-surface">
              <PrismaDarkSelector />
              <a className={styles.headerTextButton} href="/shift" aria-label="Ver turno">
                <PrismaIcon name="terminal" size={18} />
                <span>Turno</span>
              </a>
              <a className={styles.headerTextButton} href="/sync" aria-label="Ver pendientes">
                <PrismaIcon name="bell" size={18} />
                <span>Pendientes</span>
                {pendingCount > 0 ? <strong>{pendingCount}</strong> : null}
              </a>
              {status ? <div className={styles.statusArea} data-prisma-role="status-surface">{status}</div> : null}
            </div>
          </header>
          {actions ? <section className={styles.actionBand} aria-label="Acciones de pantalla" data-prisma-component="SecondaryActionCard">{actions}</section> : null}
          <div
            className={styles.content}
            data-prisma-zone={screenZone}
            data-prisma-role={screenZone ? "operational-summary" : undefined}
            data-prisma-priority={screenZone ? "primary" : undefined}
            data-prisma-state={pendingCount > 0 ? "sync_pending" : "ready"}
            data-prisma-qa={screenQa}
          >
            {children}
          </div>
        </main>
      </div>
    </>
  );
}
