import type { ReactNode } from "react";
import { PrismaIcon } from "@generated/prisma-visual-runtime/prisma-icon";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { PRISMA_TABLET_VISUAL_RUNTIME } from "@generated/prisma-visual-runtime/visual-values";
import {
  getTabletFlowCopy,
  getTabletFlowStage,
  getTabletPendingCount,
  getVisibleTabletNavItems,
  isTabletMoreActive,
  isTabletNavActive
} from "./tablet-nav";
import { TABLET_MORE_ITEMS } from "./tablet-nav";
import styles from "./prisma-tablet-shell.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

export function TabletShellStatusPill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={[styles.statusPill, styles[`status_${tone}`]].filter(Boolean).join(" ")} data-prisma-component="StatusPill">
      {children}
    </span>
  );
}

const TABLET_VISUAL_RUNTIME_CANONICAL = `${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.width}x${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.height}@${PRISMA_TABLET_VISUAL_RUNTIME.canonicalViewport.zoom}`;

function joinClasses(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function screenZoneFromPath(currentPath: string) {
  if (currentPath === "/") return "tablet-home-root";
  if (currentPath === "/pos" || currentPath === "/checkout") return "tablet-pos-root";
  if (currentPath === "/sales/today" || currentPath.startsWith("/sales/today/") || currentPath === "/sales") return "tablet-sales-root";
  if (currentPath === "/shift") return "tablet-shift-root";
  if (currentPath === "/sync" || currentPath === "/events/outbox") return "tablet-sync-root";
  if (currentPath === "/offline" || currentPath === "/settings/export" || currentPath === "/settings/license" || currentPath === "/settings/data") return "tablet-support-root";
  if (currentPath === "/returns" || currentPath.includes("/return")) return "tablet-returns-root";
  if (currentPath === "/catalog" || currentPath === "/stock" || currentPath === "/existencias" || currentPath === "/inventory" || currentPath === "/inventory/low-stock") return "tablet-catalog-root";
  return "tablet-reference-root";
}

function moreAccentFromHref(href: string) {
  if (href === "/catalog" || href === "/stock") return "amber";
  if (href === "/returns") return "magenta";
  if (href === "/shift") return "emerald";
  if (href === "/sync" || href === "/events/outbox") return "violet";
  if (href === "/offline") return "cyan";
  if (href.startsWith("/settings")) return "silver";
  return "cyan";
}

export function PrismaTabletShellUnified({
  currentPath,
  title,
  subtitle,
  kicker = "PRISMA Tablet",
  status,
  actions,
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT,
  visualSurface,
  visualPreset,
  showRouteHeader = true,
  showBottomDock = true,
  dockMode = "sticky",
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
  showRouteHeader?: boolean;
  showBottomDock?: boolean;
  dockMode?: "sticky" | "inline";
  children: ReactNode;
}) {
  const flowStage = getTabletFlowStage(currentPath);
  const flowCopy = getTabletFlowCopy(flowStage, runtimeSnapshot);
  const visibleNavItems = getVisibleTabletNavItems(currentPath, runtimeSnapshot);
  const pendingCount = getTabletPendingCount(runtimeSnapshot);
  const resolvedVisualSurface = visualSurface ?? (currentPath === "/pos" || currentPath === "/checkout" ? "tablet-pos-rifat-atlas" : "tablet-rifat-atlas");
  const resolvedVisualPreset = visualPreset ?? "PRISMA_RIFAT_ATLAS_TABLET_V1";
  const compactSellingSurface = currentPath === "/pos" || currentPath === "/checkout";
  const supportSurface = currentPath === "/settings/data" || currentPath === "/settings/export" || currentPath === "/settings/license";
  const moreActive = isTabletMoreActive(currentPath);

  return (
    <div
      className={joinClasses(styles.shell, compactSellingSurface && styles.compactSellingShell, supportSurface && styles.supportShell)}
      data-prisma-component="AppShell"
      data-prisma-product="tablet"
      data-prisma-flow-stage={flowStage}
      data-prisma-visual-surface={resolvedVisualSurface}
      data-prisma-visual-preset={resolvedVisualPreset}
      data-prisma-preset={resolvedVisualPreset}
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_RUNTIME.dataAttribute}
      data-prisma-canonical-viewport={TABLET_VISUAL_RUNTIME_CANONICAL}
      data-prisma-canonical-shell="rifat-atlas-tablet-v1"
      data-prisma-visible-upgrade="tablet-rifat-atlas-v1"
      data-prisma-background="rifat-atlas-atmosphere"
      data-prisma-support-surface={supportSurface ? "true" : undefined}
    >
      <a className={styles.skipLink} href="#contenido-principal">Saltar al contenido</a>
      <span className={styles.scene} aria-hidden="true" />

      <header className={styles.topbar} data-prisma-component="TopCommandBar" data-prisma-role="app-owner" data-prisma-layer="header">
        {supportSurface ? (
          <div className={styles.brand} aria-label="PRISMA Tablet">
            <span className={styles.brandMark} aria-hidden="true">
              <img className={styles.brandImage} src="/prisma/logo-prisma-mark-transparent.png" alt="" />
            </span>
            <span className={styles.brandText}>
              <strong>PRISMA</strong>
              <small>Tablet</small>
            </span>
          </div>
        ) : (
          <a className={styles.brand} href="/" aria-label="Ir al inicio de PRISMA Tablet">
            <span className={styles.brandMark} aria-hidden="true">
              <img className={styles.brandImage} src="/prisma/logo-prisma-mark-transparent.png" alt="" />
            </span>
            <span className={styles.brandText}>
              <strong>PRISMA</strong>
              <small>Tablet</small>
            </span>
          </a>
        )}

        {compactSellingSurface ? (
          <div className={styles.sellingMeta} aria-label="Estado operativo de venta">
            <strong>{flowCopy.label}</strong>
            <span>{pendingCount > 0 ? `${pendingCount} pendientes` : runtimeSnapshot.connection.label}</span>
          </div>
        ) : (
          supportSurface ? (
            <>
              <div className={styles.contextChips} aria-label="Contexto informativo de la Tablet">
                <span className={styles.contextChip}>
                  <PrismaIcon name="tag" size={16} />
                  <span>{runtimeSnapshot.identity.storeName}</span>
                </span>
                <span className={styles.contextChip}>
                  <PrismaIcon name="terminal" size={16} />
                  <span>{runtimeSnapshot.identity.terminalName}</span>
                </span>
                <span className={styles.contextChip}>
                  <PrismaIcon name="dashboard" size={16} />
                  <span>{runtimeSnapshot.identity.operatorName}</span>
                </span>
              </div>

              <div className={styles.topStatus} data-prisma-role="status-surface">
                <span className={styles.saleStateChip} aria-label={flowCopy.helper}>
                  <PrismaIcon name="cart" size={16} />
                  <span>{flowCopy.label}</span>
                </span>
                {status ? <div className={styles.statusArea}>{status}</div> : null}
                <a
                  className={joinClasses(styles.syncChip, pendingCount > 0 && styles.syncChipWarn)}
                  href="/sync"
                  aria-label={pendingCount > 0 ? `Abrir sincronización: ${pendingCount} pendientes` : "Abrir sincronización y notificaciones"}
                  title="Abrir sincronización y notificaciones"
                >
                  <PrismaIcon name="bell" size={18} />
                  <span>{pendingCount > 0 ? `${pendingCount} pendientes` : runtimeSnapshot.connection.label}</span>
                </a>
              </div>
            </>
          ) : (
            <>
              <div className={styles.contextChips} aria-label="Contexto de venta">
                <a className={styles.contextChip} href="/stock">
                  <PrismaIcon name="tag" size={17} />
                  <span>{runtimeSnapshot.identity.storeName}</span>
                </a>
                <a className={styles.contextChip} href="/shift">
                  <PrismaIcon name="terminal" size={17} />
                  <span>{runtimeSnapshot.identity.terminalName}</span>
                </a>
                <span className={styles.contextChip}>
                  <PrismaIcon name="dashboard" size={17} />
                  <span>{runtimeSnapshot.identity.operatorName}</span>
                </span>
              </div>

              <div className={styles.topStatus} data-prisma-role="status-surface">
                <a className={styles.saleStateChip} href="/pos" aria-label={flowCopy.helper}>
                  <PrismaIcon name="cart" size={18} />
                  <span>{flowCopy.label}</span>
                </a>
                <a className={joinClasses(styles.syncChip, pendingCount > 0 && styles.syncChipWarn)} href="/sync">
                  <PrismaIcon name="bell" size={17} />
                  <span>{pendingCount > 0 ? `${pendingCount} pendientes` : runtimeSnapshot.connection.label}</span>
                </a>
                {status ? <div className={styles.statusArea}>{status}</div> : null}
              </div>
            </>
          )
        )}
      </header>

      <main id="contenido-principal" className={styles.main} data-prisma-component="NocturneMain">
        {!compactSellingSurface && showRouteHeader ? (
          <section className={styles.titleHeader} aria-label="Pantalla actual">
            <div className={styles.titleGroup}>
              <span className={styles.kicker}>{kicker}</span>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
            {actions ? <div className={styles.actionBand} aria-label="Acciones de pantalla">{actions}</div> : null}
          </section>
        ) : actions ? (
          <div className={styles.actionBand} aria-label="Acciones de pantalla">{actions}</div>
        ) : null}

        <div
          className={styles.content}
          data-prisma-layer="content"
          data-prisma-zone={screenZoneFromPath(currentPath)}
          data-prisma-role="operational-surface"
          data-prisma-state={pendingCount > 0 ? "sync_pending" : "ready"}
        >
          {children}
        </div>
      </main>

      {showBottomDock ? (
        <nav className={joinClasses(styles.bottomDock, dockMode === "inline" && styles.bottomDockInline)} aria-label="Dock principal Tablet" data-prisma-component="TabletBottomNav" data-prisma-layer="dock">
          <div className={styles.bottomDockInner}>
            {visibleNavItems.map((item) => {
              const active = isTabletNavActive(currentPath, item.href);
              return (
                <a
                  key={`dock-${item.href}`}
                  className={active ? styles.bottomDockItemActive : styles.bottomDockItem}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  title={item.description}
                  data-prisma-component="BottomNavItem"
                  data-active={active ? "true" : undefined}
                >
                  <PrismaIcon name={item.icon} size={20} />
                  <span>{item.shortLabel}</span>
                </a>
              );
            })}
            <details className={styles.bottomDockMore} data-active={moreActive ? "true" : undefined} data-prisma-component="TabletMoreSheet">
              <summary className={moreActive ? styles.bottomDockItemActive : styles.bottomDockItem} aria-label="Abrir más secciones de Tablet">
                <PrismaIcon name="more" size={20} />
                <span>Más</span>
                {pendingCount > 0 ? <strong>{pendingCount}</strong> : null}
              </summary>
              <div className={styles.bottomDockMorePanel} aria-label="Secciones adicionales">
                <div className={styles.bottomDockMoreHeading}>
                  <span>Más secciones</span>
                  <small>Operación, continuidad y configuración</small>
                </div>
                {TABLET_MORE_ITEMS.map((item) => {
                  const active = isTabletNavActive(currentPath, item.href);
                  return (
                    <a
                      className={active ? styles.moreMenuItemActive : styles.moreMenuItem}
                      href={item.href}
                      key={item.href}
                      aria-current={active ? "page" : undefined}
                      data-prisma-accent={moreAccentFromHref(item.href)}
                    >
                      <PrismaIcon name={item.icon} size={19} />
                      <span><strong>{item.label}</strong><small>{item.description}</small></span>
                      {item.href === "/sync" && pendingCount > 0 ? <b>{pendingCount}</b> : null}
                    </a>
                  );
                })}
              </div>
            </details>
          </div>
        </nav>
      ) : null}
    </div>
  );
}
