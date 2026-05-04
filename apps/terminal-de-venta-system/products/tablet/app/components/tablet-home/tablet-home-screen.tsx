import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { buildTabletHomeViewModel } from "@/lib/tablet-home/home-view-model";
import { TabletRuntimePanel } from "@components/tablet-runtime/tablet-runtime-panel";
import styles from "./tablet-home.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

export function TabletHomeScreen({ snapshot }: Props) {
  const vm = buildTabletHomeViewModel(snapshot);

  return (
    <div className={styles.homeShell} data-prisma-component="TabletHomeScreen">
      <section className={styles.hero} aria-label="Inicio operativo">
        <div className={styles.heroMain}>
          <div className={styles.heroCopy}>
            <span>Inicio operativo</span>
            <h2>{vm.hero.title}</h2>
            <p>{vm.hero.subtitle}</p>
          </div>
          <div className={styles.heroActions}>
            <a className={styles.primaryButton} href={vm.hero.primaryHref}>{vm.hero.primaryLabel}</a>
            <a className={styles.secondaryButton} href={vm.hero.secondaryHref}>{vm.hero.secondaryLabel}</a>
          </div>
        </div>
        <div className={styles.heroAside} aria-label="Preparacion de turno">
          {vm.checklist.map((item) => (
            <div className={styles.readinessItem} key={item.label}>
              <span>
                <strong>{item.label}</strong>
                <span>{item.note}</span>
              </span>
              <i className={item.ready ? styles.readyDot : styles.warnDot} aria-hidden="true" />
            </div>
          ))}
        </div>
      </section>

      <section className={styles.metricGrid} aria-label="Metricas rapidas">
        {vm.metrics.map((metric) => (
          <article className={styles.metricCard} key={metric.label} data-tone={metric.tone}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <small>{metric.note}</small>
          </article>
        ))}
      </section>

      <section className={styles.mainGrid} aria-label="Acciones y alertas">
        <div className={styles.actionGrid}>
          {vm.actions.map((action) => (
            <a className={styles.actionCard} href={action.href} key={action.title} data-priority={action.priority} data-tone={action.tone}>
              <div>
                <h3>{action.title}</h3>
                <p>{action.description}</p>
              </div>
              <span>{action.label}</span>
            </a>
          ))}
        </div>
        <div className={styles.sideStack}>
          <TabletRuntimePanel snapshot={snapshot} />
          <aside className={styles.alertCard} aria-label="Alertas operativas">
            <h3>Alertas que sí importan</h3>
            <p>Turno, pendientes y existencias sin meter ruido de backoffice en la caja.</p>
            {vm.alerts.length ? (
              <div className={styles.alertList}>
                {vm.alerts.map((alert) => (
                  <div className={styles.alertItem} key={alert.title} data-tone={alert.tone}>
                    <strong>{alert.title}</strong>
                    <p>{alert.description}</p>
                    <a href={alert.href}>{alert.action}</a>
                  </div>
                ))}
              </div>
            ) : (
              <div className={styles.emptyAlert}>Sin alertas críticas. A vender, que el sistema no se paga solo.</div>
            )}
          </aside>
        </div>
      </section>
    </div>
  );
}
