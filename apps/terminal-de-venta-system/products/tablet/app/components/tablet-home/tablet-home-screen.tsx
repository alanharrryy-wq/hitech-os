import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { buildTabletHomeViewModel } from "@/lib/tablet-home/home-view-model";
import { TabletRuntimePanel } from "@components/tablet-runtime/tablet-runtime-panel";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import styles from "./tablet-home.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

function pendingCount(snapshot: TabletRuntimeSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export function TabletHomeScreen({ snapshot }: Props) {
  const vm = buildTabletHomeViewModel(snapshot);
  const gate = decideCanSellFromRuntimeSnapshot(snapshot);
  const shiftOpen = gate.canSell;
  const pending = pendingCount(snapshot);

  const workflowSteps = [
    { step: "1", title: shiftOpen ? "Turno abierto" : "Abrir turno", description: shiftOpen ? "Caja lista para operar con corte trazable." : "Prepara caja antes de vender para que tickets y corte salgan limpios.", href: "/shift", label: shiftOpen ? "Ver turno" : "Abrir turno", tone: shiftOpen ? "ok" : "warn" },
    { step: "2", title: shiftOpen ? "Vender" : "Caja cerrada", description: shiftOpen ? "Busca, escanea, arma el ticket y cobra sin salir del flujo POS." : gate.detail, href: shiftOpen ? "/pos" : "/shift", label: shiftOpen ? "Ir a vender" : "Abrir turno", tone: shiftOpen ? "ok" : "warn" },
    { step: "3", title: "Revisar tickets", description: "Consulta ventas cerradas, detalle y devoluciones cuando aplique.", href: "/sales/today", label: "Ventas de hoy", tone: "neutral" },
    { step: "4", title: "Cerrar o exportar", description: "Cierra turno, revisa pendientes y exporta evidencia si hace falta.", href: "/offline", label: "Soporte", tone: pending > 0 ? "warn" : "neutral" }
  ];

  const toolCards = [
    { href: "/catalog", title: "Catálogo", description: "Productos disponibles para venta local.", label: "Abrir" },
    { href: "/stock", title: "Existencias", description: "Stock operativo, quiebres y señales de reabasto.", label: "Revisar" },
    { href: "/sync", title: "Pendientes", description: pending > 0 ? `${pending} eventos por revisar.` : "Sin pendientes visibles.", label: pending > 0 ? "Atender" : "Ver" },
    { href: "/offline", title: "Sin conexión / Exportar", description: "Auditoría local, exportación y respaldo operativo.", label: "Abrir" },
    { href: "/release-gate", title: "Estado del sistema", description: "Revisión de flujos críticos antes de liberar.", label: "Ver" },
    { href: "/settings/license", title: "Licencia", description: "Estado de permisos y activación de la Tablet.", label: "Revisar" }
  ];

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
        <div className={styles.heroAside} aria-label="Preparación de turno">
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

      <section className={styles.metricGrid} aria-label="Métricas rápidas">
        {vm.metrics.map((metric) => (
          <article className={styles.metricCard} key={metric.label} data-tone={metric.tone}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <small>{metric.note}</small>
          </article>
        ))}
      </section>

      <section className={styles.workflowPanel} aria-label="Mapa de flujo de trabajo">
        <div className={styles.workflowHeader}>
          <div>
            <span>Flujo de trabajo</span>
            <h3>Todo lo importante queda a la vista</h3>
          </div>
          <p>Tablet sigue enfocada en vender, pero ya no esconde las pantallas como truco de feria.</p>
        </div>
        <div className={styles.workflowSteps}>
          {workflowSteps.map((step) => (
            <a className={styles.workflowStep} href={step.href} key={step.title} data-tone={step.tone}>
              <strong>{step.step}</strong>
              <span>
                <b>{step.title}</b>
                <small>{step.description}</small>
              </span>
              <em>{step.label} →</em>
            </a>
          ))}
        </div>
      </section>

      <section className={styles.toolPanel} aria-label="Herramientas disponibles">
        <div className={styles.workflowHeader}>
          <div>
            <span>Herramientas disponibles</span>
            <h3>Consulta y soporte sin adivinar rutas</h3>
          </div>
        </div>
        <div className={styles.toolGrid}>
          {toolCards.map((tool) => (
            <a className={styles.toolCard} href={tool.href} key={tool.href}>
              <span>
                <b>{tool.title}</b>
                <small>{tool.description}</small>
              </span>
              <em>{tool.label} →</em>
            </a>
          ))}
        </div>
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
