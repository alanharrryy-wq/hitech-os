import type { MobileDataPlaneState } from "../mobile-data-plane/types";
import { classifyInventoryState } from "../mobile-data-plane/inventory-adapter";
import type { AlertCenter, DataQualityReport, EvidenceLink, MobileAlert } from "./contracts";
import { AlertCenterSchema } from "./contracts";
import { evidence, hasEvidence } from "./evidence";

type DraftAlert = Omit<MobileAlert, "id" | "dedupeKey" | "status" | "lastSeenAt" | "priorityScore"> & {
  branchId?: string;
  ruleKey: string;
  moneyImpactWeight?: number;
  urgencyWeight?: number;
  recurrenceWeight?: number;
};

const severityWeight: Record<MobileAlert["severity"], number> = {
  critical: 5,
  high: 4,
  medium: 3,
  low: 2,
  info: 1
};

function score(alert: Pick<MobileAlert, "severity" | "confidence"> & Pick<DraftAlert, "moneyImpactWeight" | "urgencyWeight" | "recurrenceWeight">): number {
  return Math.round(
    severityWeight[alert.severity] * 40 +
    (alert.moneyImpactWeight ?? 0) * 25 +
    (alert.urgencyWeight ?? 0) * 20 +
    alert.confidence * 10 +
    (alert.recurrenceWeight ?? 0) * 5
  );
}

function normalizeAlert(draft: DraftAlert, generatedAt: string): MobileAlert {
  const evidenceItems = draft.evidence ?? [];
  const severity = (draft.severity === "critical" || draft.severity === "high") && !hasEvidence(evidenceItems) ? "medium" : draft.severity;
  const sourceRef = draft.sourceRef || draft.ruleKey;
  const branchId = draft.branchId ?? "main";
  const dedupeKey = `${draft.category}:${branchId}:${draft.source}:${sourceRef}:${draft.ruleKey}`;
  return {
    ...draft,
    severity,
    status: "new",
    id: dedupeKey.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 96),
    dedupeKey,
    priorityScore: score({ ...draft, severity }),
    lastSeenAt: generatedAt
  };
}

function dedupeAlerts(alerts: MobileAlert[]): MobileAlert[] {
  const byKey = new Map<string, MobileAlert>();
  for (const alert of alerts) {
    const current = byKey.get(alert.dedupeKey);
    if (!current || alert.priorityScore > current.priorityScore) byKey.set(alert.dedupeKey, alert);
  }
  return Array.from(byKey.values()).sort((a, b) => b.priorityScore - a.priorityScore || b.confidence - a.confidence);
}

function dataQualityAlerts(report: DataQualityReport): DraftAlert[] {
  const alerts: DraftAlert[] = [];
  const localSourceOk = report.sources.some((source) => source.id === "local" && source.status === "ok");
  for (const source of report.sources) {
    if (source.id === "local") continue;
    if (source.status === "ok") continue;
    const sourcePendingLabel = source.id === "tablet" && localSourceOk ? "heartbeat pendiente" : source.status === "unknown" ? "sin configurar" : "pendiente de certificación";
    const severity: MobileAlert["severity"] = source.id === "tablet" && source.status !== "unknown" && !localSourceOk ? "high" : source.id === "pc" ? "medium" : "low";
    const sourceEvidence = evidence(`${source.id}-status`, `${source.label} status`, source.label, source.lastError ?? source.warnings[0] ?? source.status);
    alerts.push({
      category: source.id === "tablet" ? "DEVICE" : source.id === "pc" ? "HEALTH" : "AUDIT",
      severity,
      title: `${source.label} ${sourcePendingLabel}`,
      summary: `${source.label} quedó en estado ${source.status}.`,
      whyItMatters: source.id === "tablet" && localSourceOk ? "Mobile conserva lectura operativa local; el heartbeat aún no certifica disponibilidad." : source.id === "tablet" ? "Mobile requiere fuente operativa certificada para ventas, inventario y outbox." : "La supervisión queda parcial y baja la confianza del snapshot.",
      recommendedAction: source.id === "tablet" ? "Certificar heartbeat Tablet sin tocar el proceso activo; Mobile sigue supervisando datos disponibles." : "Revisar la fuente cuando se requiera gobierno o auditoría fina.",
      source: source.label,
      sourceRef: source.id,
      confidence: report.confidence,
      evidence: [sourceEvidence],
      ruleKey: `${source.id}-source-unavailable`,
      urgencyWeight: source.id === "tablet" ? 0.8 : 0.35
    });
  }
  return alerts;
}

export function buildIntelligenceAlerts(state: MobileDataPlaneState, report: DataQualityReport): AlertCenter {
  const generatedAt = report.generatedAt;
  const drafts: DraftAlert[] = [...dataQualityAlerts(report)];

  for (const item of state.inventory.items.slice(0, 20)) {
    const stateName = classifyInventoryState(item);
    const itemEvidence: EvidenceLink[] = [
      evidence(`stock-${item.sku}`, "Stock operativo", "Tablet POS", `${item.name} ${item.sku}: ${item.stockQty} piezas, mínimo ${item.lowStockThreshold}`),
      evidence(`movement-${item.sku}`, "Movimiento", "Tablet POS", item.lastMovementLabel)
    ];
    if (stateName === "critico") {
      drafts.push({
        category: "INVENTORY",
        severity: "critical",
        title: `${item.name} sin existencia`,
        summary: `SKU ${item.sku} está en cero.`,
        whyItMatters: "Puede frenar venta inmediata o provocar venta sin existencia física.",
        recommendedAction: "Confirmar existencia física, reponer o bloquear venta del SKU en Tablet.",
        source: "Tablet POS",
        sourceRef: item.sku,
        confidence: report.confidence,
        evidence: itemEvidence,
        ruleKey: "stock-critical",
        urgencyWeight: 1,
        recurrenceWeight: item.weeklyUnitsSold > 0 ? 0.6 : 0.2
      });
    } else if (stateName === "reponer") {
      drafts.push({
        category: "INVENTORY",
        severity: "high",
        title: `${item.name} en riesgo de quiebre`,
        summary: `Quedan ${item.stockQty} piezas contra mínimo ${item.lowStockThreshold}.`,
        whyItMatters: "El producto puede quedarse sin inventario antes del siguiente pico de venta.",
        recommendedAction: "Programar reposición y confirmar stock físico.",
        source: "Tablet POS",
        sourceRef: item.sku,
        confidence: report.confidence,
        evidence: itemEvidence,
        ruleKey: "stock-reorder",
        urgencyWeight: 0.75,
        recurrenceWeight: item.weeklyUnitsSold > 0 ? 0.5 : 0.1
      });
    }
  }

  if (state.outbox.failed > 0) {
    drafts.push({
      category: "SYNC",
      severity: "high",
      title: "Sync bloqueado por eventos fallidos",
      summary: `${state.outbox.failed} eventos fallidos en outbox.`,
      whyItMatters: "La operación local puede seguir, pero PC/Core no reciben una historia limpia.",
      recommendedAction: "Reintentar sync o exportar evidencia antes del cierre.",
      source: "Tablet POS",
      sourceRef: "outbox",
      confidence: report.confidence,
      evidence: [evidence("outbox-failed", "Eventos fallidos", "Tablet POS", `${state.outbox.failed} fallidos`)],
      ruleKey: "sync-blocked",
      urgencyWeight: 0.8
    });
  } else if (state.outbox.pending > 0) {
    drafts.push({
      category: "SYNC",
      severity: "medium",
      title: "Eventos pendientes de sincronización",
      summary: `${state.outbox.pending} eventos siguen en cola.`,
      whyItMatters: "Mobile ve una operación parcial hasta que Core/PC confirmen ingestión.",
      recommendedAction: "Mantener conexión y revisar el evento pendiente más antiguo.",
      source: "Tablet POS",
      sourceRef: "outbox",
      confidence: report.confidence,
      evidence: [evidence("outbox-pending", "Eventos pendientes", "Tablet POS", `Pendientes ${state.outbox.pending}; más antiguo ${state.outbox.oldestPendingAt ?? "desconocido"}`)],
      ruleKey: "outbox-delayed",
      urgencyWeight: 0.45
    });
  }

  if (state.cash.countedCents !== null && Math.abs(state.cash.differenceCents) >= state.config.cashDifferenceWarningCents) {
    const severity: MobileAlert["severity"] = Math.abs(state.cash.differenceCents) >= state.config.cashDifferenceCriticalCents ? "high" : "medium";
    drafts.push({
      category: "MONEY",
      severity,
      title: "Diferencia de caja detectada",
      summary: `Caja difiere por ${state.cash.differenceCents} centavos.`,
      whyItMatters: "Una diferencia real de caja debe explicarse antes del corte.",
      recommendedAction: "Pedir reconteo y dejar evidencia del motivo.",
      source: "Tablet POS",
      sourceRef: "cash-current",
      confidence: report.confidence,
      evidence: [
        evidence("cash-expected", "Efectivo esperado", "Tablet POS", state.cash.expectedCents),
        evidence("cash-counted", "Efectivo contado", "Tablet POS", state.cash.countedCents)
      ],
      ruleKey: "cash-variance",
      moneyImpactWeight: Math.min(1, Math.abs(state.cash.differenceCents) / state.config.cashDifferenceCriticalCents),
      urgencyWeight: 0.75
    });
  }

  const slowProbe = state.probes.find((probe) => typeof probe.latencyMs === "number" && probe.latencyMs > 1800 && probe.ok);
  if (slowProbe) {
    drafts.push({
      category: "HEALTH",
      severity: "medium",
      title: "Latencia elevada en fuente operativa",
      summary: `${slowProbe.id} respondió en ${slowProbe.latencyMs}ms.`,
      whyItMatters: "Mobile puede abrir con lectura parcial o tardía si la fuente se degrada.",
      recommendedAction: "Revisar conectividad antes de usar el snapshot como evidencia final.",
      source: String(slowProbe.id),
      sourceRef: String(slowProbe.id),
      confidence: report.confidence,
      evidence: [evidence(`latency-${slowProbe.id}`, "Latencia", String(slowProbe.id), `${slowProbe.latencyMs}ms`)],
      ruleKey: "latency-elevated",
      urgencyWeight: 0.35
    });
  }

  if (state.salesToday.tickets === 0 && report.sources.some((source) => source.id === "tablet" && source.status === "ok")) {
    drafts.push({
      category: "SALES",
      severity: "info",
      title: "Aún no hay tickets cerrados hoy",
      summary: "Tablet respondió, pero no devolvió ventas cerradas para el día.",
      whyItMatters: "Es un vacío operativo válido, no una cifra inventada.",
      recommendedAction: "Confirmar apertura o esperar el primer ticket real.",
      source: "Tablet POS",
      sourceRef: "sales-today",
      confidence: report.confidence,
      evidence: [evidence("sales-empty", "Ventas hoy", "Tablet POS", "0 tickets reales")],
      ruleKey: "sales-empty",
      urgencyWeight: 0.1
    });
  }

  const alerts = dedupeAlerts(drafts.map((draft) => normalizeAlert(draft, generatedAt)));
  const counts = {
    total: alerts.length,
    critical: alerts.filter((alert) => alert.severity === "critical").length,
    high: alerts.filter((alert) => alert.severity === "high").length,
    medium: alerts.filter((alert) => alert.severity === "medium").length,
    low: alerts.filter((alert) => alert.severity === "low").length,
    info: alerts.filter((alert) => alert.severity === "info").length
  };
  const primaryRecommendedAction = alerts[0]?.recommendedAction ?? "Mantener supervisión normal y revisar el brief diario antes del cierre.";
  return AlertCenterSchema.parse({ alerts, counts, primaryRecommendedAction });
}
