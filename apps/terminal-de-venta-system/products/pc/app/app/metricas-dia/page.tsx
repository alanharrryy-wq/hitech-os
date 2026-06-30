import { AppShell } from "@components/layout/app-shell";
import { SmartDropdownDock } from "@components/uiux/smart-dropdown-dock";
import styles from "./metricas-dia.module.css";

export const dynamic = "force-dynamic";

const financeSignals = [
  {
    label: "Venta del día",
    value: "$42,860",
    note: "Lectura accionable, no tarjeta decorativa",
    action: "Abrir ledger de ventas",
    href: "/sales-control"
  },
  {
    label: "Tickets",
    value: "128",
    note: "Volumen por cajero, terminal y tablet",
    action: "Filtrar tickets",
    href: "/sales-control"
  },
  {
    label: "Ticket promedio",
    value: "$334",
    note: "Útil para detectar caída o ticket inflado",
    action: "Comparar periodo",
    href: "/sales-control"
  },
  {
    label: "Diferencia caja",
    value: "Revisar",
    note: "Debe terminar en motivo y evidencia",
    action: "Ir a caja",
    href: "/cash-sessions"
  }
];

const analysisRows = [
  {
    area: "Efectivo",
    lectura: "Confirmar contado físico antes del cierre",
    riesgo: "Faltante o sobrante sin motivo",
    siguiente: "Preparar cierre guiado"
  },
  {
    area: "Tarjeta",
    lectura: "Conciliar contra terminal y folio",
    riesgo: "Venta aprobada sin confirmación",
    siguiente: "Abrir tickets del día"
  },
  {
    area: "Transferencia",
    lectura: "Validar referencia y responsable",
    riesgo: "Pago no conciliado",
    siguiente: "Exportar evidencia"
  },
  {
    area: "Sync",
    lectura: "Revisar tablet, caja y folio",
    riesgo: "Venta atrasada o duplicada",
    siguiente: "Abrir sincronización"
  }
];

const actionRail = [
  { label: "Abrir ventas y caja", href: "/sales-control", primary: true },
  { label: "Revisar sesiones", href: "/cash-sessions" },
  { label: "Exportar reportes", href: "/exportables" },
  { label: "Revisar sync", href: "/sync-operativo" }
];

export default function MetricasDiaPage() {
  return (
    <AppShell currentPath="/metricas-dia">
      <main className={styles.dailyFinanceCanvas} data-prisma-surface="pc-daily-finance-readout">
        <section className={styles.hero}>
          <div>
            <span className={styles.kicker}>lectura financiera diaria</span>
            <h1>Métricas del día</h1>
            <p>Una consola compacta para entender ventas, caja, métodos de pago y diferencias antes del cierre.</p>
          </div>
          <a href="/sales-control">Abrir ledger operativo</a>
        </section>

        <section className={styles.canvasGrid}>
          <aside className={styles.filterRail} aria-label="Filtros y acciones de métricas">
            <SmartDropdownDock currentPath="/metricas-dia" title="Filtros diarios" />

            <section className={styles.actionRail} data-prisma-component="PcDailyFinanceActionRail">
              <span className={styles.kicker}>acciones</span>
              <h2>La métrica termina en operación</h2>
              <div>
                {actionRail.map((action) => (
                  <a key={action.label} className={action.primary ? styles.primaryAction : undefined} href={action.href}>
                    {action.label}
                  </a>
                ))}
              </div>
            </section>
          </aside>

          <section className={styles.readoutMain} aria-label="Lectura financiera del día">
            <section className={styles.financeStrip} data-prisma-component="PcDailyFinanceStrip">
              <div className={styles.mainSignal}>
                <span className={styles.kicker}>venta vigilada</span>
                <strong>{financeSignals[0].value}</strong>
                <small>{financeSignals[0].note}</small>
              </div>
              <div className={styles.signalStack}>
                {financeSignals.slice(1).map((signal) => (
                  <article key={signal.label}>
                    <span>{signal.label}</span>
                    <strong>{signal.value}</strong>
                    <small>{signal.note}</small>
                    <a href={signal.href}>{signal.action}</a>
                  </article>
                ))}
              </div>
            </section>

            <section className={styles.cashRibbon} data-prisma-component="PcDailyCashDifferenceRibbon">
              <div>
                <span className={styles.kicker}>diferencia</span>
                <h2>Antes de cerrar, caja debe explicar la variación</h2>
                <p>Esperado, contado, diferencia, motivo, responsable y evidencia. Si falta endpoint auditable, la acción queda bloqueada honestamente.</p>
              </div>
              <a href="/cash-sessions">Preparar caja</a>
            </section>

            <section className={styles.analysisLedger} data-prisma-component="PcDailyMetricLedger">
              <div className={styles.sectionHead}>
                <span className={styles.kicker}>ledger analítico</span>
                <h2>Lectura por área</h2>
                <p>Cada fila tiene riesgo y siguiente paso. Nada de numeritos presumidos sin utilidad.</p>
              </div>
              <div className={styles.analysisTable} role="table" aria-label="Lectura operativa de métricas">
                <div role="row" className={styles.tableHead}>
                  <span>Área</span>
                  <span>Lectura</span>
                  <span>Riesgo</span>
                  <span>Siguiente paso</span>
                </div>
                {analysisRows.map((row) => (
                  <div role="row" key={row.area} className={styles.tableRow}>
                    <strong>{row.area}</strong>
                    <span>{row.lectura}</span>
                    <span>{row.riesgo}</span>
                    <span>{row.siguiente}</span>
                  </div>
                ))}
              </div>
            </section>
          </section>
        </section>
      </main>
    </AppShell>
  );
}
