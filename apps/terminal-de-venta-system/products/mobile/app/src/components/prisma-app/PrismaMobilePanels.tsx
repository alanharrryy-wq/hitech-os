import type { PrismaMobileAction, PrismaMobileAlert, PrismaMobileBranch, PrismaMobileCashCurrentPayload, PrismaMobileInventoryItem, PrismaMobileReportCard, PrismaMobileSalesPoint } from "@/lib/prisma-app/prisma-app-api-contracts";
import type { ChartViewModel } from "@/lib/prisma-app/mobile-intelligence/contracts";
import { formatSignedMxnFromCents, safePercentHeight } from "@/lib/prisma-app/prisma-mobile-formatters";
import styles from "./prisma-mobile-dashboard.module.css";

const priorityClass: Record<PrismaMobileAction["priority"], string> = { alta: styles.priorityHigh, media: styles.priorityMedium, baja: styles.priorityLow };
const alertClass: Record<PrismaMobileAlert["severity"], string> = { critica: styles.alertCritical, alta: styles.alertHigh, media: styles.alertMedium, info: styles.alertInfo };
const inventoryClass: Record<PrismaMobileInventoryItem["state"], string> = { critico: styles.inventoryCritical, reponer: styles.inventoryReorder, normal: styles.inventoryNormal, sobrestock: styles.inventoryOverstock };
const branchClass: Record<PrismaMobileBranch["status"], string> = { sano: styles.branchHealthy, revisar: styles.branchReview, urgente: styles.branchUrgent, offline: styles.branchOffline };

export function PrismaMobileActionPanel({ actions }: { actions: PrismaMobileAction[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-actions-title" data-prisma-zone="mobile-review-first"><header><span>Acciones sugeridas</span><h2 id="mobile-actions-title">Qué revisar primero</h2><p className={styles.optionalAdderBoundaryMicro}>Son sugerencias de supervisión premium: Mobile no bloquea POS ni operación base.</p></header><div className={styles.actionList}>{actions.map((action, index) => <article key={`${action.title}-${index}`}><b>{index + 1}</b><div><strong>{action.title}</strong><span>{action.detail}</span><small>{action.owner}</small></div><em className={priorityClass[action.priority]}>{action.priority}</em></article>)}</div></section>;
}

export function PrismaMobileSalesChart({ chart, points }: { chart: ChartViewModel | null; points?: PrismaMobileSalesPoint[] }) {
  const chartPoints = chart?.points ?? points?.map((point) => ({ x: point.hour, y: point.amountCents, label: point.label, status: "ok" as const, meta: { amount: point.amount, height: point.height } })) ?? [];
  const max = Math.max(0, ...chartPoints.map((point) => typeof point.y === "number" ? point.y : 0));
  return <section className={styles.panelCard} aria-labelledby="mobile-sales-title"><header><span>Ventas</span><h2 id="mobile-sales-title">{chart?.title ?? "Ritmo por horario"}</h2></header><div className={styles.salesChart} aria-label="Venta por horario">{chartPoints.map((point) => { const height = typeof point.meta.height === "number" ? `${point.meta.height}%` : typeof point.meta.height === "string" ? point.meta.height : max > 0 && typeof point.y === "number" ? `${Math.round((point.y / max) * 100)}%` : "0%"; const amount = typeof point.meta.amount === "string" ? point.meta.amount : typeof point.y === "number" ? String(point.y) : "sin dato"; return <article key={point.x}><i style={{ height: safePercentHeight(height) }} /><strong>{point.label}</strong><span>{amount}</span></article>; })}</div></section>;
}

export function PrismaMobileCashPanel({ cash }: { cash: PrismaMobileCashCurrentPayload }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-cash-title"><header><span>Caja · vista opcional</span><h2 id="mobile-cash-title">Lectura de caja sin operar POS</h2><p className={styles.optionalAdderBoundaryMicro}>Mobile supervisa; Tablet Solo vende sola y conserva cobro, corte, ticket y operación offline.</p></header><div className={styles.cashGrid}><article><span>Esperado</span><strong>{cash.expectedLabel}</strong></article><article><span>Contado</span><strong>{cash.countedLabel}</strong></article><article><span>Diferencia</span><strong>{formatSignedMxnFromCents(cash.differenceCents)}</strong></article></div><div className={styles.cashMovements}>{cash.movements.map((movement) => <p key={`${movement.label}-${movement.detail}`}><span>{movement.label}</span><strong>{movement.value}</strong><small>{movement.detail}</small></p>)}</div></section>;
}

export function PrismaMobileInventoryPanel({ items }: { items: PrismaMobileInventoryItem[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-inventory-title"><header><span>Inventario</span><h2 id="mobile-inventory-title">Productos a vigilar</h2></header><div className={styles.inventoryList}>{items.map((item) => <article key={item.sku}><div><strong>{item.name}</strong><span>{item.sku} · {item.category} · {item.weeklyUnitsSold} u/semana</span></div><aside><strong>{item.stock}</strong><em className={inventoryClass[item.state]}>{item.state}</em></aside></article>)}</div></section>;
}

export function PrismaMobileAlertsPanel({ alerts }: { alerts: PrismaMobileAlert[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-alerts-title"><header><span>Alertas</span><h2 id="mobile-alerts-title">Excepciones activas</h2></header><div className={styles.alertList}>{alerts.map((alert) => <article key={alert.id} className={alertClass[alert.severity]}><div><strong>{alert.title}</strong><span>{alert.area} · {alert.time}</span><p>{alert.detail}</p></div><em>{alert.severity}</em></article>)}</div></section>;
}

export function PrismaMobileReportsPanel({ cards }: { cards: PrismaMobileReportCard[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-reports-title"><header><span>Reportes · supervisor opcional</span><h2 id="mobile-reports-title">Resumen ejecutivo móvil</h2><p className={styles.optionalAdderBoundaryMicro}>PC y Mobile son adders opcionales. Internet no es requisito para venta base Tablet Solo.</p></header><div className={styles.reportGrid}>{cards.map((card) => <article key={card.title}><span>{card.title}</span><strong>{card.value}</strong><p>{card.detail}</p><small>{card.footnote}</small></article>)}</div></section>;
}

export function PrismaMobileBranchesPanel({ branches }: { branches: PrismaMobileBranch[] }) {
  return <section className={styles.panelCard} aria-labelledby="mobile-branches-title"><header><span>MultiSucursal</span><h2 id="mobile-branches-title">Salud por tienda</h2></header><div className={styles.branchList}>{branches.map((branch) => <article key={branch.name} className={branchClass[branch.status]}><div><strong>{branch.name}</strong><span>{branch.tickets} tickets · sync {branch.syncLag}</span></div><aside><strong>{branch.salesToday}</strong><em>{branch.status}</em></aside></article>)}</div></section>;
}
