import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { buildTabletHomeViewModel } from "@/lib/tablet-home/home-view-model";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import { QuickActionGrid, QuickActionTile, type QuickActionTone } from "@components/tablet-action-tiles/tablet-action-tiles";
import styles from "./tablet-home.module.css";

type Props = {
  snapshot: TabletRuntimeSnapshot;
};

function pendingCount(snapshot: TabletRuntimeSnapshot) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

type HomeQuickCard = {
  href: string;
  title: string;
  description: string;
  label: string;
  icon: PrismaIconName;
  tone: QuickActionTone;
  owner: string;
};

export function TabletHomeScreen({ snapshot }: Props) {
  const vm = buildTabletHomeViewModel(snapshot);
  const gate = decideCanSellFromRuntimeSnapshot(snapshot);
  const shiftOpen = gate.canSell;
  const pending = pendingCount(snapshot);

  const quickCards: HomeQuickCard[] = [
    { href: shiftOpen ? "/pos" : "/shift", title: shiftOpen ? "Vender" : "Abrir turno", description: shiftOpen ? "Busca productos, arma el ticket y cobra." : gate.detail, label: shiftOpen ? "Vender" : "Abrir", icon: shiftOpen ? "cart" : "terminal", tone: shiftOpen ? "primary" : "warning", owner: "pos-shift" },
    { href: "/catalog?new=1", title: "Nuevo producto", description: "Abre el formulario real de catálogo para registrar producto vendible.", label: "Crear", icon: "plus", tone: "inventory", owner: "catalog" },
    { href: "/stock", title: "Inventario", description: "Revisa existencias y productos con pocas piezas.", label: "Revisar", icon: "package", tone: snapshot.catalog.lowStockProducts > 0 ? "warning" : "inventory", owner: "stock" },
    { href: "/sales/today", title: "Ventas de hoy", description: "Consulta tickets cerrados y totales del dia.", label: "Ver", icon: "receipt", tone: "neutral", owner: "sales" },
    { href: "/sync", title: "Pendientes", description: pending > 0 ? `${pending} pendientes por atender.` : "Todo al dia.", label: pending > 0 ? "Atender" : "Ver", icon: "bell", tone: pending > 0 ? "warning" : "success", owner: "sync" },
    { href: "/settings/license", title: "Licencia", description: "Confirma si la Tablet puede operar.", label: "Estado", icon: "settings", tone: "license", owner: "license" }
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
        {/* 09D: readiness checklist is already represented in the runtime rail; do not duplicate it vertically on Home. */}
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

      <section className={styles.toolPanel} aria-label="Accesos principales">
        <div className={styles.workflowHeader}>
          <div>
            <span>Accesos principales</span>
            <h3>Lo necesario para operar</h3>
          </div>
          <p>Acciones rapidas para venta, creación de producto, inventario, tickets, pendientes y licencia en una sola lectura.</p>
        </div>
        <QuickActionGrid label="Acciones rapidas de inicio" density="wide">
          {quickCards.map((tool) => (
            <QuickActionTile
              key={tool.href}
              href={tool.href}
              title={tool.title}
              description={tool.description}
              actionLabel={tool.label}
              icon={tool.icon}
              tone={tool.tone}
              owner={tool.owner}
              kind={tool.title === "Nuevo producto" ? "quick-create" : "surface-action"}
            />
          ))}
        </QuickActionGrid>
      </section>

      <aside className={styles.alertCard} aria-label="Alertas operativas">
        <h3>Alertas importantes</h3>
        <p>Turno, pendientes y existencias sin ruido extra en la caja.</p>
        {vm.alerts.length ? (
          <div className={styles.alertList}>
            {vm.alerts.slice(0, 3).map((alert) => (
              <div className={styles.alertItem} key={alert.title} data-tone={alert.tone}>
                <strong>{alert.title}</strong>
                <p>{alert.description}</p>
                <a href={alert.href}>{alert.action}</a>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.emptyAlert}>Sin alertas criticas. Puedes continuar vendiendo con respaldo local disponible.</div>
        )}
      </aside>
    </div>
  );
}
