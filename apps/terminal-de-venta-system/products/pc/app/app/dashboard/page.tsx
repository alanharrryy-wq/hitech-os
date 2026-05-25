import styles from "./hoy-premium.module.css";
import { getOperationWorkspace } from "@/server/services/operation-control.service";
import type { OperationAlert, OperationWorkspace, Severity } from "@/modules/operations/types";

export const dynamic = "force-dynamic";

type HoyRow = {
  pending: string;
  severity: string;
  tone: "danger" | "warning" | "info" | "ok";
  detail: string;
  action: string;
  href: string;
};

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 0
  }).format(Math.round(cents / 100));
}

function freshnessLabel(value: string) {
  if (!value) return "Actualización no disponible";
  const date = new Date(value);
  if (!Number.isNaN(date.getTime())) {
    return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
  }
  return value;
}

function severityTone(severity: Severity): HoyRow["tone"] {
  if (severity === "CRITICO") return "danger";
  if (severity === "ALTO" || severity === "MEDIO") return "warning";
  return "ok";
}

function severityLabel(severity: Severity) {
  if (severity === "CRITICO") return "Crítico";
  if (severity === "ALTO") return "Atención";
  if (severity === "MEDIO") return "Revisar";
  return "Bajo";
}

function severityIcon(severity: Severity) {
  if (severity === "CRITICO") return "●";
  if (severity === "ALTO" || severity === "MEDIO") return "●";
  return "●";
}

function actionText(alert: OperationAlert) {
  const moduleName = alert.module.toLowerCase();
  if (moduleName.includes("sync")) return "Sincronizar";
  if (moduleName.includes("reabasto")) return "Ver reabasto";
  if (moduleName.includes("compra")) return "Ver compra";
  if (moduleName.includes("recepción") || moduleName.includes("recepcion")) return "Ver recepción";
  return "Revisar";
}

function buildRows(workspace: OperationWorkspace): HoyRow[] {
  const alertRows = workspace.alerts.slice(0, 5).map((alert) => ({
    pending: alert.title,
    severity: severityLabel(alert.severity),
    tone: severityTone(alert.severity),
    detail: alert.detail,
    action: actionText(alert),
    href: alert.href
  }));

  if (alertRows.length > 0) return alertRows;

  const kpiRows = workspace.kpis
    .filter((kpi) => kpi.status === "warning" || kpi.status === "critical")
    .slice(0, 5)
    .map((kpi) => ({
      pending: kpi.label,
      severity: kpi.status === "critical" ? "Crítico" : "Atención",
      tone: kpi.status === "critical" ? "danger" as const : "warning" as const,
      detail: kpi.note || kpi.range,
      action: "Ver detalle",
      href: kpi.href
    }));

  if (kpiRows.length > 0) return kpiRows;

  return [
    {
      pending: "Operación",
      severity: "Bien",
      tone: "ok",
      detail: "No hay pendientes críticos detectados en la lectura actual.",
      action: "Ver detalle",
      href: "/dashboard"
    }
  ];
}

function recommendedAction(workspace: OperationWorkspace) {
  const critical = workspace.alerts.find((alert) => alert.severity === "CRITICO" || alert.severity === "ALTO");
  if (critical) {
    return {
      eyebrow: "Prioridad detectada",
      title: critical.title,
      detail: critical.detail,
      primaryHref: critical.href,
      primaryLabel: actionText(critical)
    };
  }

  if (workspace.summary.highPrioritySignals > 0) {
    return {
      eyebrow: "Inventario con presión",
      title: "Revisa productos críticos antes de crear pedidos.",
      detail: "Motivo: hay señales de reabasto con prioridad alta y conviene atenderlas antes de comprar.",
      primaryHref: "/replenishment",
      primaryLabel: "Ver reabasto"
    };
  }

  if (workspace.summary.receiptsWithDiscrepancy > 0) {
    return {
      eyebrow: "Recepción pendiente",
      title: "Revisa recepciones con diferencia.",
      detail: "Motivo: una recepción incompleta puede afectar existencias y compras.",
      primaryHref: "/receiving",
      primaryLabel: "Ver recepción"
    };
  }

  return {
    eyebrow: "Operación estable",
    title: "La operación no muestra bloqueos principales.",
    detail: "Motivo: la lectura actual no detecta pendientes críticos; puedes revisar ventas o descargar resumen.",
    primaryHref: "/sales-control",
    primaryLabel: "Ver ventas"
  };
}

function confidenceText(workspace: OperationWorkspace) {
  if (workspace.meta.confidence === "real") return "Datos reales";
  if (workspace.meta.confidence === "partial") return "Datos incompletos";
  if (workspace.meta.confidence === "proxy") return "Estimación operativa";
  if (workspace.meta.confidence === "missing") return "Sin lectura suficiente";
  return "Lectura bloqueada";
}

function healthLabel(workspace: OperationWorkspace, urgentCount: number) {
  if (workspace.meta.confidence === "blocked") return { label: "Sin datos disponibles", tone: "warning" as const };
  if (urgentCount > 0) return { label: "Requiere atención", tone: "danger" as const };
  return { label: "Operación estable", tone: "ok" as const };
}

function miniSummary(workspace: OperationWorkspace) {
  return [
    { label: "Venta neta", value: money(workspace.summary.netSalesCents), note: `${workspace.summary.tickets} tickets`, href: "/sales-control" },
    { label: "Reabasto", value: String(workspace.summary.replenishmentSignals), note: `${workspace.summary.highPrioritySignals} de prioridad alta`, href: "/replenishment" },
    { label: "Recepción", value: String(workspace.summary.receiptsWithDiscrepancy), note: "con diferencia", href: "/receiving" }
  ];
}

export default async function HoyPage() {
  const workspace = await getOperationWorkspace("dashboard");
  const rows = buildRows(workspace);
  const clearOperation = rows.length === 1 && rows[0]?.tone === "ok" && rows[0]?.pending === "Operación";
  const action = recommendedAction(workspace);
  const urgentCount = workspace.alerts.filter((alert) => alert.severity === "CRITICO" || alert.severity === "ALTO").length;
  const reviewCount = workspace.alerts.filter((alert) => alert.severity === "MEDIO").length + workspace.summary.openOrders + workspace.summary.receiptsWithDiscrepancy;
  const okSignals = workspace.kpis.filter((kpi) => kpi.status === "ok").length;
  const health = healthLabel(workspace, urgentCount);
  const updated = freshnessLabel(workspace.meta.generatedAt);
  const urgencyMeter = Math.min(100, Math.max(12, urgentCount * 24 + reviewCount * 8));

  return (
    <section className={styles.page} aria-labelledby="hoy-title" data-prisma-screen="hoy" data-prisma-contract="ansi-decision-center" data-prisma-visual="cloudglass-layer-pack-01" data-prisma-background="fractured-graphite-cloudglass">
      <div className={styles.scene} aria-hidden="true" />

      <header className={styles.heroShell}>
        <div className={styles.heroGlow} aria-hidden="true" />
        <div className={styles.heroCopy}>
          <p className={styles.kicker}>HOY</p>
          <h1 id="hoy-title" className={styles.title}>Hoy</h1>
          <p className={styles.subtitle}>Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.</p>
          <div className={styles.statusLine} aria-label="Estado general de operación">
            <span className={`${styles.statusPill} ${styles[health.tone]}`}>
              <span className={styles.pulseDot} aria-hidden="true" />
              Estado general: {health.label}
            </span>
            <span className={styles.statusPill}>Actualizado: {updated}</span>
            <span className={styles.statusPill}>{confidenceText(workspace)}</span>
          </div>
        </div>

        <aside className={styles.heroPanel} aria-label="Pulso ejecutivo de hoy">
          <div className={styles.orbitBadge}>
            <span>{urgentCount > 0 ? "⚠" : "✓"}</span>
          </div>
          <p className={styles.panelLabel}>Pulso del día</p>
          <strong>{urgentCount > 0 ? `${urgentCount} asuntos urgentes` : "Sin bloqueo principal"}</strong>
          <div className={styles.meter} aria-label={`Presión operativa ${urgencyMeter}%`}>
            <span style={{ width: `${urgencyMeter}%` }} />
          </div>
          <p>{reviewCount} puntos para revisar antes de cerrar operación.</p>
        </aside>
      </header>

      <section className={styles.summaryGrid} aria-label="Lectura rápida de Hoy">
        <article className={`${styles.summaryCard} ${styles.urgentCard}`}>
          <div className={styles.cardTopline}>
            <span className={styles.redOrb} aria-hidden="true" />
            <h2>Urgente</h2>
          </div>
          <strong>{urgentCount}</strong>
          <p>alertas críticas o altas</p>
          <ul>
            <li>{workspace.summary.highPrioritySignals} señales altas de reabasto</li>
            <li>{workspace.summary.receiptsWithDiscrepancy} recepciones con diferencia</li>
          </ul>
        </article>

        <article className={`${styles.summaryCard} ${styles.reviewCard}`}>
          <div className={styles.cardTopline}>
            <span className={styles.amberOrb} aria-hidden="true" />
            <h2>Revisar</h2>
          </div>
          <strong>{reviewCount}</strong>
          <p>pendientes operativos</p>
          <ul>
            <li>{workspace.summary.openOrders} pedidos abiertos</li>
            <li>{workspace.summary.replenishmentSignals} productos con señal de reabasto</li>
          </ul>
        </article>

        <article className={`${styles.summaryCard} ${styles.okCard}`}>
          <div className={styles.cardTopline}>
            <span className={styles.greenOrb} aria-hidden="true" />
            <h2>Bien</h2>
          </div>
          <strong>{okSignals}</strong>
          <p>indicadores sin alerta</p>
          <ul>
            <li>Venta neta: {money(workspace.summary.netSalesCents)}</li>
            <li>{confidenceText(workspace)}</li>
          </ul>
        </article>
      </section>

      <section className={styles.actionShell} aria-labelledby="hoy-action-title">
        <div className={styles.actionHalo} aria-hidden="true" />
        <div className={styles.actionCopy}>
          <p className={styles.actionKicker}>ACCIÓN RECOMENDADA</p>
          <h2 id="hoy-action-title">{action.title}</h2>
          <p>{action.detail}</p>
        </div>
        <div className={styles.actionButtons}>
          <a href={action.primaryHref} className={styles.primaryButton}>{action.primaryLabel}</a>
          <a href="/replenishment" className={styles.secondaryButton}>Ver reabasto</a>
          <a href="/sales-control" className={styles.secondaryButton}>Descargar resumen</a>
        </div>
      </section>

      <section className={styles.microGrid} aria-label="Indicadores de apoyo">
        {miniSummary(workspace).map((item) => (
          <a href={item.href} className={styles.microCard} key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.note}</small>
          </a>
        ))}
      </section>

      <section className={styles.tablePanel} aria-labelledby="hoy-pending-title" data-prisma-component="event-horizon-ledger">
        <div className={styles.ledgerBackdrop} aria-hidden="true" />
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.kicker}>Detalle operativo</p>
            <h2 id="hoy-pending-title">Pendientes principales</h2>
          </div>
          <div className={styles.ledgerHeaderActions} aria-label="Estado del ordenamiento de pendientes">
            <span className={styles.tableHint}>Ordenado por gravedad</span>
            <span className={styles.ledgerMode}>Signal stack</span>
          </div>
        </div>

        {clearOperation ? (
          <div className={styles.clearLedger} role="status" aria-label="Operación sin pendientes principales">
            <div className={styles.clearGlyph} aria-hidden="true">
              <span />
            </div>
            <div className={styles.clearCopy}>
              <p className={styles.clearEyebrow}>Lectura limpia</p>
              <h3>Operación despejada</h3>
              <p>{rows[0].detail}</p>
            </div>
            <div className={styles.clearMetrics} aria-label="Indicadores de soporte sin bloqueo principal">
              <span><strong>{money(workspace.summary.netSalesCents)}</strong><small>venta neta</small></span>
              <span><strong>{workspace.summary.openOrders}</strong><small>pedidos abiertos</small></span>
              <span><strong>{workspace.summary.receiptsWithDiscrepancy}</strong><small>recepciones con diferencia</small></span>
            </div>
            <div className={styles.clearActions}>
              <a className={styles.tableAction} href="/sales-control">Ver ventas</a>
              <a className={styles.ghostAction} href="/dashboard">Ver detalle</a>
            </div>
          </div>
        ) : (
          <div className={styles.ledgerGrid} role="list" aria-label="Pendientes operativos ordenados por gravedad">
            {rows.map((row, index) => (
              <article
                className={`${styles.ledgerItem} ${styles[`ledgerItem_${row.tone}`]}`}
                data-tone={row.tone}
                role="listitem"
                key={`${row.pending}-${row.href}`}
              >
                <div className={styles.ledgerIndex} aria-hidden="true">{String(index + 1).padStart(2, "0")}</div>
                <div className={styles.ledgerSignal} aria-hidden="true">
                  <span>{severityIcon(row.severity as Severity)}</span>
                </div>
                <div className={styles.ledgerMain}>
                  <div className={styles.ledgerTitleRow}>
                    <strong>{row.pending}</strong>
                    <span className={`${styles.rowBadge} ${styles[row.tone]}`}>
                      <span aria-hidden="true">●</span>
                      {row.severity}
                    </span>
                  </div>
                  <p>{row.detail}</p>
                </div>
                <a className={styles.tableAction} href={row.href}>{row.action}</a>
              </article>
            ))}
          </div>
        )}
      </section>

      <details className={styles.evidencePanel}>
        <summary>Ver evidencia técnica</summary>
        <div className={styles.evidenceGrid}>
          <p><strong>Fuente:</strong> {workspace.meta.persistence === "available" ? "Base principal" : "Sin datos disponibles"}</p>
          <p><strong>Persistencia:</strong> {workspace.meta.persistence === "available" ? "Disponible" : "No disponible"}</p>
          <p><strong>Confianza:</strong> {confidenceText(workspace)}</p>
          <p><strong>Última lectura:</strong> {updated}</p>
          {workspace.meta.warnings.length > 0 ? (
            <ul>
              {workspace.meta.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p>No hay advertencias técnicas en la lectura actual.</p>
          )}
        </div>
      </details>
    </section>
  );
}
