import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { getCatalogPressureLabel, getPendingEventsLabel, getRuntimeHeaderLine, getRuntimeModeLabel, getRuntimeOperatorLine } from "@/lib/tablet-runtime-snapshot/view-model";
import styles from "@components/tablet-shell/prisma-tablet-shell.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
  variant?: "full" | "compact";
  currentPath?: string;
};

function Chip({ label, value, tone, href }: { label: string; value: string; tone: string; href: string }) {
  return (
    <a className={[styles.runtimeChip, styles[`runtime_${tone}`]].join(" ")} href={href} data-prisma-component="RuntimeChip" data-prisma-runtime-chip-tone={tone}>
      <span className={styles.runtimeChipLabel}>{label}</span>
      <span className={styles.runtimeChipValueRow}>
        <strong>{value}</strong>
        <i className={styles.runtimeChipDot} aria-hidden="true" />
      </span>
    </a>
  );
}

function isSupportStatusContext(currentPath?: string) {
  if (!currentPath) return false;
  return currentPath === "/sync"
    || currentPath === "/events/outbox"
    || currentPath === "/offline"
    || currentPath === "/settings/export"
    || currentPath === "/settings/license"
    || currentPath === "/settings"
    || currentPath.startsWith("/support")
    || currentPath.startsWith("/diagnostics")
    || currentPath.startsWith("/license")
    || currentPath.startsWith("/settings/");
}

export function TabletRuntimeStatusStrip({ snapshot, variant = "full", currentPath }: Props) {
  const compact = variant === "compact";
  const supportStatusContext = isSupportStatusContext(currentPath);
  const syncState =
    snapshot.connection.failedEvents > 0 || snapshot.connection.conflictEvents > 0
      ? "sync_failed"
      : snapshot.connection.pendingEvents > 0
        ? "sync_pending"
        : "ready";
  return (
    <section
      className={[styles.runtimeStrip, compact ? styles.runtimeStripCompact : ""].filter(Boolean).join(" ")}
      aria-label="Estado operativo de la Tablet"
      data-prisma-component="RuntimeStatusStrip"
      data-prisma-zone="tablet-pos-sync-status"
      data-prisma-role="status-surface"
      data-prisma-state={syncState}
      data-prisma-motion="sync-feedback"
      data-prisma-qa="tablet-qa-sync"
      data-variant={variant}
      data-prisma-runtime-layout={compact ? "rail" : "full"}
    >
      <div className={styles.runtimeIdentity}>
        <span>{getRuntimeModeLabel(snapshot)}</span>
        <strong>{getRuntimeHeaderLine(snapshot)}</strong>
        <small>{getRuntimeOperatorLine(snapshot)}</small>
      </div>
      <div className={styles.runtimeChips} data-prisma-support-context={supportStatusContext ? "true" : undefined}>
        {supportStatusContext ? (
          <>
            <Chip label="Soporte" value={snapshot.connection.label} tone={snapshot.connection.tone} href={snapshot.connection.actionHref} />
            <Chip label="Pendientes" value={getPendingEventsLabel(snapshot)} tone={snapshot.connection.tone} href="/sync" />
            <Chip label="Catálogo" value={getCatalogPressureLabel(snapshot)} tone={snapshot.catalog.tone} href={snapshot.catalog.actionHref} />
          </>
        ) : (
          <>
            <Chip label="Turno" value={snapshot.shift.label} tone={snapshot.shift.tone} href={snapshot.shift.actionHref} />
            <Chip label="Conexión" value={snapshot.connection.label} tone={snapshot.connection.tone} href={snapshot.connection.actionHref} />
            <Chip label="Pendientes" value={getPendingEventsLabel(snapshot)} tone={snapshot.connection.tone} href="/sync" />
            <Chip label="Catálogo" value={getCatalogPressureLabel(snapshot)} tone={snapshot.catalog.tone} href={snapshot.catalog.actionHref} />
          </>
        )}
      </div>
    </section>
  );
}
