import type { ReactNode } from "react";
import { PrismaCommandDock } from "./prisma-command-dock";
import { PrismaGlassControl } from "./prisma-glass-control";
import { PrismaLiquidAction } from "./prisma-liquid-action";
import { PrismaSoftCard } from "./prisma-soft-card";
import { PrismaStatusChip } from "./prisma-status-chip";
import { PRISMA_TABLET_VISUAL_V2 } from "./tablet-visual-tokens";
import styles from "./prisma-route-surface.module.css";

export type TabletSurfaceIntent =
  | "catalog"
  | "customer"
  | "detail"
  | "form"
  | "generic"
  | "home"
  | "inventory"
  | "pos"
  | "report"
  | "sales"
  | "settings"
  | "sync";

export type PrismaRouteMetric = {
  label: string;
  value: ReactNode;
  detail?: ReactNode;
};

export type PrismaRouteAction = {
  href?: string;
  label: string;
  sublabel?: string;
};

type PrismaRouteSurfaceProps = {
  actions?: ReactNode;
  children: ReactNode;
  description: ReactNode;
  emptyState?: ReactNode;
  intent?: TabletSurfaceIntent;
  metrics?: PrismaRouteMetric[];
  primaryAction?: PrismaRouteAction;
  rail?: ReactNode;
  routeId: string;
  statusLabel?: ReactNode;
  title: ReactNode;
};

function routeGlyph(intent: TabletSurfaceIntent) {
  const glyphs: Record<TabletSurfaceIntent, string> = {
    catalog: "CAT",
    customer: "CLI",
    detail: "DET",
    form: "CFG",
    generic: "OPS",
    home: "INI",
    inventory: "STK",
    pos: "POS",
    report: "REP",
    sales: "VTA",
    settings: "SET",
    sync: "SYN"
  };
  return glyphs[intent] ?? "OPS";
}

function defaultMetrics(routeId: string, intent: TabletSurfaceIntent): PrismaRouteMetric[] {
  return [
    { label: "Modo", value: "Operativo", detail: "Controles táctiles" },
    { label: "Vista", value: routeId, detail: intent }
  ];
}

export function PrismaSurfaceHeader({
  actions,
  description,
  intent = "generic",
  primaryAction,
  routeId,
  statusLabel = "Lista",
  title
}: Omit<PrismaRouteSurfaceProps, "children" | "emptyState" | "metrics" | "rail">) {
  const actionNode = primaryAction ? (
    <PrismaLiquidAction icon={<span>{routeGlyph(intent)}</span>} sublabel={primaryAction.sublabel} fullWidth>{primaryAction.label}</PrismaLiquidAction>
  ) : null;

  return (
    <header className={styles.routeHeader} data-prisma-component="PrismaSurfaceHeader" data-prisma-layer="header" data-prisma-effect="softglass-surface rim-light">
      <div className={styles.routeTitleBlock}>
        <span className={styles.routeGlyph} aria-hidden="true">{routeGlyph(intent)}</span>
        <div className={styles.routeCopy}>
          <div className={styles.routeMeta}>
            <span className={styles.routeKicker}>Terminal Tablet</span>
            <PrismaStatusChip>{statusLabel}</PrismaStatusChip>
          </div>
          <h2 className={styles.routeTitle}>{title}</h2>
          <p className={styles.routeDescription}>{description}</p>
        </div>
      </div>
      <div className={styles.routeActions} data-prisma-route-owner={routeId}>
        {actions}
        {actionNode}
      </div>
    </header>
  );
}

export function PrismaSurfacePanel({ children, emptyState, routeId }: { children: ReactNode; emptyState?: ReactNode; routeId: string }) {
  return (
    <section className={styles.contentPanel} data-prisma-component="PrismaSurfacePanel" data-prisma-route-owner={routeId} data-prisma-layer="content" data-prisma-effect="softglass-surface inner-highlight surface-breathing-glow">
      {children}
      {emptyState ? (
        <PrismaSoftCard className={styles.emptyState} data-prisma-empty-state="true">
          <div className={styles.emptyStateInner}>{emptyState}</div>
        </PrismaSoftCard>
      ) : null}
    </section>
  );
}

export function PrismaRouteSurface({
  actions,
  children,
  description,
  emptyState,
  intent = "generic",
  metrics,
  primaryAction,
  rail,
  routeId,
  statusLabel,
  title
}: PrismaRouteSurfaceProps) {
  const resolvedMetrics = metrics ?? defaultMetrics(routeId, intent);
  const hasRail = Boolean(rail) || resolvedMetrics.length > 0;

  return (
    <section
      className={styles.routeSurface}
      data-prisma-component="PrismaRouteSurface"
      data-prisma-route-owner={routeId}
      data-prisma-surface-component="PrismaRouteSurface"
      data-prisma-visual-v2={PRISMA_TABLET_VISUAL_V2.dataAttribute}
      data-prisma-layer="surface"
      data-prisma-effect="softglass-surface selected-pulse focus-halo"
      data-intent={intent}
    >
      <PrismaSurfaceHeader
        actions={actions}
        description={description}
        intent={intent}
        primaryAction={primaryAction}
        routeId={routeId}
        statusLabel={statusLabel}
        title={title}
      />
      <div className={styles.surfaceGrid} data-has-rail={hasRail ? "true" : "false"}>
        <PrismaSurfacePanel emptyState={emptyState} routeId={routeId}>
          {children}
        </PrismaSurfacePanel>
        {hasRail ? (
          <aside className={styles.surfaceRail} data-prisma-layer="surface" data-prisma-effect="softglass-surface selected-pulse">
            {rail}
            {resolvedMetrics.map((metric) => (
              <PrismaSoftCard key={String(metric.label)} className={styles.metricCard} tone="amount">
                <span className={styles.metricLabel}>{metric.label}</span>
                <strong className={styles.metricValue}>{metric.value}</strong>
                {metric.detail ? <span className={styles.metricDetail}>{metric.detail}</span> : null}
              </PrismaSoftCard>
            ))}
            <PrismaGlassControl label="Vista activa" hint="Tablet">
              <input aria-label={`Vista activa ${routeId}`} value={routeId} readOnly />
            </PrismaGlassControl>
          </aside>
        ) : null}
      </div>
      <PrismaCommandDock className={styles.routeDock} aria-label={`Accesos operativos de ${routeId}`} data-prisma-layer="dock">
        <a href="/pos">Vender</a>
        <a href="/stock">Stock</a>
        <a href="/sync">Pendientes</a>
      </PrismaCommandDock>
    </section>
  );
}
