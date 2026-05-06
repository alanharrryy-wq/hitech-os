import type { PrismaMobileAction, PrismaMobileAlert, PrismaMobileBranch, PrismaMobileCashCurrentPayload, PrismaMobileInventoryItem, PrismaMobileReportCard, PrismaMobileSalesPoint } from "@/lib/prisma-app/prisma-app-api-contracts";
import { formatSignedMxnFromCents, safePercentHeight } from "@/lib/prisma-app/prisma-mobile-formatters";
import styles from "./prisma-mobile-dashboard.module.css";

const priorityClass: Record<PrismaMobileAction["priority"], string> = { alta: styles.priorityHigh, media: styles.priorityMedium, baja: styles.priorityLow };
const alertClass: Record<PrismaMobileAlert["severity"], string> = { critica: styles.alertCritical, alta: styles.alertHigh, media: styles.alertMedium, info: styles.alertInfo };
const inventoryClass: Record<PrismaMobileInventoryItem["state"], string> = { critico: styles.inventoryCritical, reponer: styles.inventoryReorder, normal: styles.inventoryNormal, sobrestock: styles.inventoryOverstock };
const branchClass: Record<PrismaMobileBranch["status"], string> = { sano: styles.branchHealthy, revisar: styles.branchReview, urgente: styles.branchUrgent, offline: styles.branchOffline };

export function PrismaMobileActionPanel({ actions }: { actions: PrismaMobileAction[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-actions-title"><header><span>Acciones sugeridas</span><h2 id="mobile-actions-title">Qué revisar primero</h2></header><div className={styles.actionList}>{actions.map((action, index) => <article key={`${action.title}-${index}`}><b>{index + 1}</b><div><strong>{action.title}</strong><span>{action.detail}</span><small>{action.owner}</small></div><em className={priorityClass[action.priority]}>{action.priority}</em></article>)}</div></section>;
}

export function PrismaMobileSalesChart({ points }: { points: PrismaMobileSalesPoint[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-sales-title"><header><span>Ventas</span><h2 id="mobile-sales-title">Ritmo por horario</h2></header><div className={styles.salesChart} aria-label="Venta por horario">{points.map((point) => <article key={point.hour}><i style={{ height: safePercentHeight(point.height) }} /><strong>{point.label}</strong><span>{point.amount}</span></article>)}</div></section>;
}

export function PrismaMobileCashPanel({ cash }: { cash: PrismaMobileCashCurrentPayload }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-cash-title"><header><span>Caja</span><h2 id="mobile-cash-title">Corte y efectivo</h2></header><div className={styles.cashGrid}><article><span>Esperado</span><strong>{cash.expectedLabel}</strong></article><article><span>Contado</span><strong>{cash.countedLabel}</strong></article><article><span>Diferencia</span><strong>{formatSignedMxnFromCents(cash.differenceCents)}</strong></article></div><div className={styles.cashMovements}>{cash.movements.map((movement) => <p key={`${movement.label}-${movement.detail}`}><span>{movement.label}</span><strong>{movement.value}</strong><small>{movement.detail}</small></p>)}</div></section>;
}

export function PrismaMobileInventoryPanel({ items }: { items: PrismaMobileInventoryItem[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-inventory-title"><header><span>Inventario</span><h2 id="mobile-inventory-title">Productos a vigilar</h2></header><div className={styles.inventoryList}>{items.map((item) => <article key={item.sku}><div><strong>{item.name}</strong><span>{item.sku} · {item.category} · {item.weeklyUnitsSold} u/semana</span></div><aside><strong>{item.stock}</strong><em className={inventoryClass[item.state]}>{item.state}</em></aside></article>)}</div></section>;
}

export function PrismaMobileAlertsPanel({ alerts }: { alerts: PrismaMobileAlert[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-alerts-title"><header><span>Alertas</span><h2 id="mobile-alerts-title">Excepciones activas</h2></header><div className={styles.alertList}>{alerts.map((alert) => <article key={alert.id} className={alertClass[alert.severity]}><div><strong>{alert.title}</strong><span>{alert.area} · {alert.time}</span><p>{alert.detail}</p></div><em>{alert.severity}</em></article>)}</div></section>;
}

export function PrismaMobileReportsPanel({ cards }: { cards: PrismaMobileReportCard[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-reports-title"><header><span>Reportes</span><h2 id="mobile-reports-title">Corte ejecutivo</h2></header><div className={styles.reportGrid}>{cards.map((card) => <article key={card.title}><span>{card.title}</span><strong>{card.value}</strong><p>{card.detail}</p><small>{card.footnote}</small></article>)}</div></section>;
}

export function PrismaMobileBranchesPanel({ branches }: { branches: PrismaMobileBranch[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-branches-title"><header><span>MultiSucursal</span><h2 id="mobile-branches-title">Salud por tienda</h2></header><div className={styles.branchList}>{branches.map((branch) => <article key={branch.name} className={branchClass[branch.status]}><div><strong>{branch.name}</strong><span>{branch.tickets} tickets · sync {branch.syncLag}</span></div><aside><strong>{branch.salesToday}</strong><em>{branch.status}</em></aside></article>)}</div></section>;
}
