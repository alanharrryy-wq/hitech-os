import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { getCatalogPressureLabel, getPendingEventsLabel, getRuntimeHeaderLine, getRuntimeModeLabel, getRuntimeOperatorLine } from "@/lib/tablet-runtime-snapshot/view-model";
import styles from "@components/tablet-shell/prisma-tablet-shell.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

function Chip({ label, value, tone, href }: { label: string; value: string; tone: string; href: string }) {
  return (
    <a className={[styles.runtimeChip, styles[`runtime_${tone}`]].join(" ")} href={href} data-prisma-component="RuntimeChip">
      <span>{label}</span>
      <strong>{value}</strong>
    </a>
  );
}

export function TabletRuntimeStatusStrip({ snapshot }: Props) {
  return (
    <section className={styles.runtimeStrip} aria-label="Estado operativo de la Tablet" data-prisma-component="RuntimeStatusStrip">
      <div className={styles.runtimeIdentity}>
        <span>{getRuntimeModeLabel(snapshot)}</span>
        <strong>{getRuntimeHeaderLine(snapshot)}</strong>
        <small>{getRuntimeOperatorLine(snapshot)}</small>
      </div>
      <div className={styles.runtimeChips}>
        <Chip label="Turno" value={snapshot.shift.label} tone={snapshot.shift.tone} href={snapshot.shift.actionHref} />
        <Chip label="Conexion" value={snapshot.connection.label} tone={snapshot.connection.tone} href={snapshot.connection.actionHref} />
        <Chip label="Pendientes" value={getPendingEventsLabel(snapshot)} tone={snapshot.connection.tone} href="/sync" />
        <Chip label="Catalogo" value={getCatalogPressureLabel(snapshot)} tone={snapshot.catalog.tone} href={snapshot.catalog.actionHref} />
      </div>
    </section>
  );
}
