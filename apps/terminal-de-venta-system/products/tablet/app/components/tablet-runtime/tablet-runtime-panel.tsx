import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { buildRuntimeAuditSummary, compactRuntimeDateTime, formatRuntimeMoney } from "@/lib/tablet-runtime-snapshot/view-model";
import styles from "@components/tablet-shell/prisma-tablet-shell.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

export function TabletRuntimePanel({ snapshot }: Props) {
  const audit = buildRuntimeAuditSummary(snapshot);
  return (
    <aside className={styles.runtimePanel} aria-label="Resumen operativo" data-prisma-component="RuntimePanel">
      <div className={styles.runtimePanelHeader}>
        <span>Estado vivo</span>
        <strong>{audit.visibleState.shift}</strong>
      </div>
      <dl className={styles.runtimeMetricGrid}>
        <div>
          <dt>Ventas del dia</dt>
          <dd>{formatRuntimeMoney(snapshot.sales.totalCents)}</dd>
        </div>
        <div>
          <dt>Tickets</dt>
          <dd>{snapshot.sales.ticketsClosed}</dd>
        </div>
        <div>
          <dt>Productos activos</dt>
          <dd>{snapshot.catalog.activeProducts}</dd>
        </div>
        <div>
          <dt>Ultimo movimiento</dt>
          <dd>{compactRuntimeDateTime(snapshot.catalog.lastMovementAt)}</dd>
        </div>
      </dl>
      {snapshot.warnings.length ? (
        <ul className={styles.runtimeWarnings}>
          {snapshot.warnings.map((warning) => <li key={warning}>{warning}</li>)}
        </ul>
      ) : null}
    </aside>
  );
}
