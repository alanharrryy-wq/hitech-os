import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { PRISMA_TABLET_VISUAL_V2 } from "../tablet-visual-v2/tablet-visual-tokens";
import {
  getTabletFlowCopy,
  getTabletFlowStage,
  getTabletPendingCount,
  getVisibleTabletNavItems,
  isTabletNavActive
} from "./tablet-nav";
import styles from "./prisma-tablet-shell.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

export function TabletShellStatusPill({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={[styles.statusPill, styles[`status_${tone}`]].filter(Boolean).join(" ")} data-prisma-component="StatusPill">
      {children}
    </span>
  );
}

const TABLET_VISUAL_V2_CANONICAL = `${PRISMA_TABLET_VISUAL_V2.canonicalViewport.width}x${PRISMA_TABLET_VISUAL_V2.canonicalViewport.height}@${PRISMA_TABLET_VISUAL_V2.canonicalViewport.zoom}`;

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
  showBottomDock?: boolean;
  dockMode?: "sticky" | "inline";
  children: ReactNode;
}) {
  const flowStage = getTabletFlowStage(currentPath);
  const flowCopy = getTabletFlowCopy(flowStage, runtimeSnapshot);
  const visibleNavItems = getVisibleTabletNavItems(currentPath, runtimeSnapshot);
  const pendingCount = getTabletPendingCount(runtimeSnapshot);
  const resolvedVisualSurface = visualSurface ?? (currentPath === "/pos" || currentPath === "/checkout" ? "tablet-pos" : "tablet-softglass");
  const resolvedVisualPreset = visualPreset ?? "PRISMA_SOFTGLASS_REFERENCE_2606";
  const compactSellingSurface = currentPath === "/pos" || currentPath === "/checkout";
  const dockItems = visibleNavItems.filter((item) =>
    ["/pos", "/shift", "/stock", "/sales/today", "/returns", "/sync", "/settings/license"].includes(item.href)
  );
  const moreLinks = [
    { href: "/settings/license", label: "Configuracion", description: "Licencia, equipo y continuidad", icon: "settings" as const },
    { href: "/settings/export", label: "Exportaciones", description: "Ventas, pendientes y movimientos", icon: "save" as const },
    { href: "/offline", label: "Modo offline", description: "Respaldo local y auditoria", icon: "bell" as const },
    { href: "/prisma-pulse", label: "Estado operativo", description: "Lectura de salud de la Tablet", icon: "dashboard" as const },
    { href: "/settings/license#license-support", label: "Soporte", description: "Detalle visible para soporte", icon: "users" as const },
    { href: "/inventory/low-stock", label: "Stock bajo", description: "Productos que requieren atencion", icon: "package" as const },
    { href: "/sales/history", label: "Historial", description: "Tickets locales anteriores", icon: "chart" as const }
  ];

  return (
    <div
      className={joinClasses(styles.shell, compactSellingSurface && styles.compactSellingShell)}
      data-prisma-component="AppShell"
      data-prisma-product="tablet"
      data-prisma-flow-stage={flowStage}
      data-prisma-visual-surface={resolvedVisualSurface}
      data-prisma-visual-preset={resolvedVisualPreset}
      data-prisma-preset={resolvedVisualPreset}
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
      data-prisma-canonical-viewport={TABLET_VISUAL_V2_CANONICAL}
      data-prisma-canonical-shell="softglass-reference-2606"
      data-prisma-visible-upgrade="tablet-softglass-canonical-2606"
      data-prisma-background="softglass-reference-image"
    >
      <a className={styles.skipLink} href="#contenido-principal">Saltar al contenido</a>
      <span className={styles.scene} aria-hidden="true" />

      <header className={styles.topbar} data-prisma-component="TopCommandBar" data-prisma-role="app-owner" data-prisma-layer="header">
        <a className={styles.brand} href="/pos" aria-label="Ir a vender en PRISMA POS">
          <span className={styles.brandMark} aria-hidden="true">
            <img className={styles.brandImage} src="/prisma/logo-prisma-mark-transparent.png" alt="" />
          </span>
          <span className={styles.brandText}>
            <strong>PRISMA</strong>
            <small>Tablet</small>
          </span>
        </a>

        {compactSellingSurface ? (
          <div className={styles.sellingMeta} aria-label="Estado operativo de venta">
            <strong>{flowCopy.label}</strong>
            <span>{pendingCount > 0 ? `${pendingCount} pendientes` : runtimeSnapshot.connection.label}</span>
          </div>
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
              <details className={styles.moreMenu} data-prisma-component="TabletMoreMenu">
                <summary aria-label="Abrir mas acciones de Tablet">
                  <PrismaIcon name="more" size={18} />
                  <span>Mas</span>
                </summary>
                <div className={styles.moreMenuPanel}>
                  {moreLinks.map((item) => (
                    <a className={styles.moreMenuItem} href={item.href} key={item.href}>
                      <PrismaIcon name={item.icon} size={18} />
                      <span>
                        <strong>{item.label}</strong>
                        <small>{item.description}</small>
                      </span>
                    </a>
                  ))}
                </div>
              </details>
              {status ? <div className={styles.statusArea}>{status}</div> : null}
            </div>
          </>
        )}
      </header>

      <main id="contenido-principal" className={styles.main} data-prisma-component="SoftglassMain">
        {!compactSellingSurface ? (
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
            {dockItems.map((item) => {
              const active = isTabletNavActive(currentPath, item.href);
              const showPendingBadge = item.href === "/sync" && pendingCount > 0;
              return (
                <a
                  key={`dock-${item.href}`}
                  className={active ? styles.bottomDockItemActive : styles.bottomDockItem}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  title={item.description}
                  data-prisma-component="BottomNavItem"
                  data-active={active ? "true" : undefined}
                  data-attention={showPendingBadge ? "true" : undefined}
                >
                  <PrismaIcon name={item.icon} size={20} />
                  <span>{item.shortLabel}</span>
                  {showPendingBadge ? <strong>{pendingCount}</strong> : null}
                </a>
              );
            })}
          </div>
        </nav>
      ) : null}
    </div>
  );
}
