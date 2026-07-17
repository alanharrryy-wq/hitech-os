import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { buildTabletHomeViewModel } from "@/lib/tablet-home/home-view-model";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import styles from "./tablet-home.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

function pendingCount(snapshot: TabletRuntimeSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

type HomeLink = {
  href: string;
  title: string;
  description: string;
  label: string;
};

export function OperationalHomeWorkspace({ snapshot }: Props) {
  const vm = buildTabletHomeViewModel(snapshot);
  const gate = decideCanSellFromRuntimeSnapshot(snapshot);
  const shiftOpen = gate.canSell;
  const pending = pendingCount(snapshot);

  const homeLinks: HomeLink[] = [
    { href: "/stock", title: "Inventario", description: snapshot.catalog.lowStockProducts > 0 ? `${snapshot.catalog.lowStockProducts} producto(s) con stock bajo.` : "Existencias listas para vender.", label: "Revisar" },
    { href: "/sales/today", title: "Ventas de hoy", description: "Consulta tickets cerrados y totales del día.", label: "Ver ventas" },
    { href: "/sync", title: "Pendientes", description: pending > 0 ? `${pending} movimiento(s) requieren atención.` : "La cola local está al día.", label: pending > 0 ? "Atender" : "Ver estado" },
    { href: "/catalog?new=1", title: "Catálogo", description: "Busca o registra un producto vendible.", label: "Abrir catálogo" }
  ];

  return (
    <div className={styles.homeShell} data-prisma-component="TabletHomeScreen"
      data-surface="tablet"
      data-screen="tablet_home"
      data-zone="pos"
      data-panel="tablet-home-screen"
      data-target="tablet-home-screen-panel-42"
      data-kind="panel"
      data-role="revenue-core"
    >
      <section className={styles.hero} aria-label="Inicio operativo"
        data-surface="tablet"
        data-screen="tablet_home"
        data-zone="pos"
        data-panel="tablet-home-screen"
        data-target="tablet-home-screen-inicio-operativo-43"
        data-kind="text"
        data-role="copy"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-div-1" data-kind="panel" data-role="container" className={styles.heroMain}>
          <div className={styles.heroCopy}
            data-surface="tablet"
            data-screen="tablet_home"
            data-zone="pos"
            data-panel="tablet-home-screen"
            data-target="tablet-home-screen-text-45"
            data-kind="text"
            data-role="copy"
          >
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-span-2" data-kind="text" data-role="text">Inicio operativo</span>
            <h1
              data-surface="tablet"
              data-screen="tablet_home"
              data-zone="pos"
              data-panel="tablet-home-screen"
              data-target="tablet-home-screen-text-47"
              data-kind="text"
              data-role="copy"
            >{vm.hero.title}</h1>
            <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-p-3" data-kind="text" data-role="text">{vm.hero.subtitle}</p>
          </div>
          <div className={styles.heroActions}
            data-surface="tablet"
            data-screen="tablet_home"
            data-zone="pos"
            data-panel="tablet-home-screen"
            data-target="tablet-home-screen-button-50"
            data-kind="button"
            data-role="action"
          >
            <a className={styles.primaryButton} href={vm.hero.primaryHref}
              data-surface="tablet"
              data-screen="tablet_home"
              data-zone="pos"
              data-panel="tablet-home-screen"
              data-target="tablet-home-screen-button-51"
              data-kind="button"
              data-role="action"
            >{vm.hero.primaryLabel}</a>
            <a className={styles.secondaryButton} href={vm.hero.secondaryHref}
              data-surface="tablet"
              data-screen="tablet_home"
              data-zone="pos"
              data-panel="tablet-home-screen"
              data-target="tablet-home-screen-button-52"
              data-kind="button"
              data-role="action"
            >{vm.hero.secondaryLabel}</a>
          </div>
        </div>
        {/* 09D: readiness checklist is already represented in the runtime rail; do not duplicate it vertically on Home. */}
      </section>

      <section className={styles.metricGrid} aria-label="Métricas rápidas"
        data-surface="tablet"
        data-screen="tablet_home"
        data-zone="pos"
        data-panel="tablet-home-screen"
        data-target="tablet-home-screen-m-tricas-r-pidas-58"
        data-kind="text"
        data-role="copy"
      >
        {vm.metrics.map((metric) => (
          <article className={styles.metricCard} key={metric.label} data-tone={metric.tone}
            data-surface="tablet"
            data-screen="tablet_home"
            data-zone="pos"
            data-panel="tablet-home-screen"
            data-target="tablet-home-screen-panel-60"
            data-kind="panel"
            data-role="revenue-core"
          >
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-span-4" data-kind="text" data-role="text">{metric.label}</span>
            <strong
              data-surface="tablet"
              data-screen="tablet_home"
              data-zone="pos"
              data-panel="tablet-home-screen"
              data-target="tablet-home-screen-element-62"
              data-kind="element"
              data-role="revenue-core"
            >{metric.value}</strong>
            <small>{metric.note}</small>
          </article>
        ))}
      </section>

      <section className={styles.toolPanel} aria-label="Accesos principales"
        data-surface="tablet"
        data-screen="tablet_home"
        data-zone="pos"
        data-panel="tablet-home-screen"
        data-target="tablet-home-screen-accesos-principales-68"
        data-kind="panel"
        data-role="revenue-core"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-div-5" data-kind="panel" data-role="container" className={styles.workflowHeader}>
          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-div-6" data-kind="panel" data-role="container">
            <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-span-7" data-kind="text" data-role="text">Accesos principales</span>
            <h3
              data-surface="tablet"
              data-screen="tablet_home"
              data-zone="pos"
              data-panel="tablet-home-screen"
              data-target="tablet-home-screen-text-72"
              data-kind="text"
              data-role="copy"
            >Lo necesario para operar</h3>
          </div>
          <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-p-8" data-kind="text" data-role="text">Acciones rapidas para venta, creación de producto, inventario, tickets, pendientes y licencia en una sola lectura.</p>
        </div>
        <div className={styles.workflowLinks}>
          {homeLinks.map((tool) => (
            <a className={styles.workflowLink} key={tool.href} href={tool.href}>
              <span><strong>{tool.title}</strong><small>{tool.description}</small></span>
              <b>{tool.label}</b>
            </a>
          ))}
        </div>
      </section>

      <aside className={styles.alertCard} aria-label="Alertas operativas"
        data-surface="tablet"
        data-screen="tablet_home"
        data-zone="pos"
        data-panel="tablet-home-screen"
        data-target="tablet-home-screen-alertas-operativas-93"
        data-kind="panel"
        data-role="revenue-core"
      >
        <h3
          data-surface="tablet"
          data-screen="tablet_home"
          data-zone="pos"
          data-panel="tablet-home-screen"
          data-target="tablet-home-screen-text-94"
          data-kind="text"
          data-role="copy"
        >Alertas importantes</h3>
        <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-p-9" data-kind="text" data-role="text">Turno, pendientes y existencias sin ruido extra en la caja.</p>
        {vm.alerts.length ? (
          <div className={styles.alertList}
            data-surface="tablet"
            data-screen="tablet_home"
            data-zone="pos"
            data-panel="tablet-home-screen"
            data-target="tablet-home-screen-table-97"
            data-kind="table"
            data-role="data-display"
          >
            {vm.alerts.slice(0, 3).map((alert) => (
              <div className={styles.alertItem} key={alert.title} data-tone={alert.tone}
                data-surface="tablet"
                data-screen="tablet_home"
                data-zone="pos"
                data-panel="tablet-home-screen"
                data-target="tablet-home-screen-cart-99"
                data-kind="cart"
                data-role="revenue-core"
              >
                <strong
                  data-surface="tablet"
                  data-screen="tablet_home"
                  data-zone="pos"
                  data-panel="tablet-home-screen"
                  data-target="tablet-home-screen-element-100"
                  data-kind="element"
                  data-role="revenue-core"
                >{alert.title}</strong>
                <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-p-10" data-kind="text" data-role="text">{alert.description}</p>
                <a data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="tablet_home_screen" data-target="tablet-home-screen-a-11" data-kind="button" data-role="button" href={alert.href}>{alert.action}</a>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.emptyAlert}
            data-surface="tablet"
            data-screen="tablet_home"
            data-zone="pos"
            data-panel="tablet-home-screen"
            data-target="tablet-home-screen-text-107"
            data-kind="text"
            data-role="copy"
          >Sin alertas criticas. Puedes continuar vendiendo con respaldo local disponible.</div>
        )}
      </aside>
    </div>
  );
}

export const TabletHomeScreen = OperationalHomeWorkspace;
