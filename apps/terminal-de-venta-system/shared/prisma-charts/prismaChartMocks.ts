import type {
  ActionPriorityStackDatum,
  CausalFlowRibbonDatum,
  ConfidenceBand,
  DecisionLedgerPoint,
  FreshnessBeacon,
  HealthRadarAxis,
  IncidentSparkCard,
  InventoryRiskNode,
  OperationalDensityCell,
  OperationalWaterfallStep,
  OwnerPulsePoint,
  PrismaMobileChartsViewModel,
  PrismaPcChartsViewModel,
  PrismaTabletChartsViewModel,
  ServiceDependencyEdge,
  ServiceDependencyNode,
  ShiftPulseBucket,
  SyncOutboxMatrixCell
} from "./prismaChartContracts";

export const PRISMA_CHART_MOCK_GENERATED_AT = "2026-05-11T08:00:00.000Z";

function iso(minutesAgo: number) {
  return new Date(Date.parse(PRISMA_CHART_MOCK_GENERATED_AT) - minutesAgo * 60_000).toISOString();
}


const operationalDensityFieldMock: OperationalDensityCell[] = ["Cloudflare", "Sync", "Inventory", "POS", "Workers"].flatMap((moduleName, moduleIndex) =>
  ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"].map((label, bucketIndex) => ({
    bucketStart: iso(360 - bucketIndex * 45),
    bucketEnd: iso(330 - bucketIndex * 45),
    bucketLabel: label,
    moduleId: moduleName.toLowerCase(),
    moduleName,
    eventCount: 3 + moduleIndex + bucketIndex,
    warnCount: (moduleIndex + bucketIndex) % 3,
    errorCount: moduleName === "Cloudflare" && bucketIndex > 2 ? 2 : moduleName === "Inventory" && bucketIndex === 4 ? 3 : 0,
    avgLatencyMs: 80 + moduleIndex * 24 + bucketIndex * 18,
    staleMinutesAvg: moduleName === "Sync" ? 12 + bucketIndex * 4 : bucketIndex,
    retryCount: moduleName === "Sync" ? bucketIndex * 2 : moduleIndex,
    pressureScore: Math.min(96, 16 + moduleIndex * 9 + bucketIndex * 7 + (moduleName === "Inventory" && bucketIndex === 4 ? 24 : 0)),
    dominantCause: moduleName === "Sync" ? "retry_storm" : moduleName === "Cloudflare" ? "route_probe" : "normal_pressure",
    confidence: 52 + moduleIndex * 5,
    state: moduleName === "Inventory" && bucketIndex === 4 ? "anomaly" : moduleName === "Cloudflare" && bucketIndex > 2 ? "peak" : "normal",
    anomalyLabel: moduleName === "Inventory" && bucketIndex === 4 ? "Stock pressure spike" : undefined,
    actionHint: moduleName === "Inventory" && bucketIndex === 4 ? "Prepare reorder decision with evidence" : undefined,
    evidenceRef: moduleName === "Inventory" && bucketIndex === 4 ? "mock:inventory:pressure:12" : undefined
  }))
);

const operationalDensityHeatmapModules = [
  "Plataforma Web",
  "API Gateway",
  "Autenticación",
  "Pagos",
  "Inventario",
  "Órdenes",
  "Notificaciones",
  "Reportes",
  "Integraciones",
  "Data Pipeline"
] as const;

const operationalDensityHeatmapBuckets = Array.from({ length: 49 }, (_item, index) => `${String(Math.floor(index / 2)).padStart(2, "0")}:${index % 2 === 0 ? "00" : "30"}`);

function operationalDensityBaseScore(moduleIndex: number, bucketIndex: number) {
  const hour = bucketIndex / 2;
  const midday = Math.exp(-Math.pow(hour - 12.35, 2) / 14) * (30 + moduleIndex * 1.45);
  const morning = Math.exp(-Math.pow(hour - 8.35, 2) / 9) * (15 + (moduleIndex % 4) * 3.8);
  const evening = Math.exp(-Math.pow(hour - 19.15, 2) / 10) * (18 + ((9 - moduleIndex) % 5) * 2.9);
  const diagonalBand = Math.exp(-Math.pow(hour - (6.35 + moduleIndex * 0.82), 2) / 6.5) * (11 + moduleIndex * 0.95);
  const gatewayHotspot = Math.exp(-Math.pow(hour - 12.5, 2) / 0.55 - Math.pow(moduleIndex - 1.0, 2) / 0.75) * 34;
  const paymentsHotspot = Math.exp(-Math.pow(hour - 19.5, 2) / 0.70 - Math.pow(moduleIndex - 3.0, 2) / 0.95) * 38;
  const reportingWarmRidge = Math.exp(-Math.pow(hour - 10.5, 2) / 5.8 - Math.pow(moduleIndex - 7.2, 2) / 4.8) * 24;
  const microTexture =
    Math.sin(hour * 1.13 + moduleIndex * 0.91) * 2.7 +
    Math.cos(hour * 0.67 - moduleIndex * 1.21) * 1.8;
  const base = 10 + moduleIndex * 1.62 + Math.sin((hour + moduleIndex * 0.65) / 1.75) * 4.4;
  return Math.round(Math.max(5, Math.min(99, base + midday + morning + evening + diagonalBand + gatewayHotspot + paymentsHotspot + reportingWarmRidge + microTexture)));
}

const operationalDensityHeatmapMock: OperationalDensityCell[] = operationalDensityHeatmapModules.flatMap((moduleName, moduleIndex) =>
  operationalDensityHeatmapBuckets.map((bucketLabel, bucketIndex) => {
    const spike = moduleName === "API Gateway" && bucketLabel === "12:30" ? 16 : moduleName === "Pagos" && bucketLabel === "19:30" ? 18 : 0;
    const pressureScore = Math.min(100, operationalDensityBaseScore(moduleIndex, bucketIndex) + spike);
    const isGatewayPeak = moduleName === "API Gateway" && bucketLabel === "12:30";
    const isPaymentsAnomaly = moduleName === "Pagos" && bucketLabel === "19:30";
    const state = isGatewayPeak || isPaymentsAnomaly ? "anomaly" : pressureScore < 18 ? "cold" : "normal";
    const anomalyLabel = isGatewayPeak
      ? "Pico de carga 12:45"
      : isPaymentsAnomaly
        ? "Anomalía detectada 19:32"
        : undefined;
    return {
      bucketStart: `2026-05-11T${bucketLabel === "24:00" ? "23:59" : bucketLabel}:00.000Z`,
      bucketEnd: `2026-05-11T${bucketLabel === "24:00" ? "23:59" : bucketLabel}:59.000Z`,
      bucketLabel,
      moduleId: moduleName.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
      moduleName,
      eventCount: Math.max(1, Math.round(pressureScore / 5) + moduleIndex + (bucketIndex % 5)),
      warnCount: pressureScore > 68 ? 2 + ((moduleIndex + bucketIndex) % 3) : pressureScore > 44 ? 1 : 0,
      errorCount: state === "anomaly" ? 3 : pressureScore > 84 ? 1 : 0,
      avgLatencyMs: 55 + pressureScore * 3 + moduleIndex * 9,
      staleMinutesAvg: pressureScore > 84 ? 18 + moduleIndex : pressureScore > 66 ? 8 + (bucketIndex % 5) : bucketIndex % 3,
      retryCount: state === "anomaly" ? 8 + moduleIndex : pressureScore > 82 ? 3 + (bucketIndex % 3) : bucketIndex % 2,
      pressureScore,
      dominantCause: state === "anomaly" ? "capacity_spike" : pressureScore > 82 ? "load_concentration" : pressureScore < 18 ? "low_activity" : "normal_pressure",
      confidence: Math.min(97, 60 + Math.round(pressureScore / 4)),
      state,
      anomalyLabel,
      actionHint: isGatewayPeak
        ? "Escalar gateway y revisar colas antes de promoción"
        : isPaymentsAnomaly
          ? "Revisar pagos, latencia y evidencia de transacciones"
          : pressureScore > 76
            ? "Mantener vigilancia activa"
            : "Sin acción inmediata",
      evidenceRef: anomalyLabel ? `mock:ops-heatmap:${moduleName}:${bucketLabel}` : undefined
    };
  })
);

export const mockPcCharts: PrismaPcChartsViewModel = {
  causalFlowRibbon: [
    { sourceModule: "Cloudflare", causeType: "public_route_404", effectType: "degraded_health", actionTarget: "Review DNS config", weight: 34, severity: "ERROR", confidence: 72, evidenceCount: 4, incidentIds: ["inc_cf_404"], firstSeenAt: iso(180), lastSeenAt: iso(12), ownerRole: "Infra" },
    { sourceModule: "Sync", causeType: "retry_storm", effectType: "stale_snapshot", actionTarget: "Review PC ingest", weight: 29, severity: "WARN", confidence: 64, evidenceCount: 3, incidentIds: ["inc_sync_retry"], firstSeenAt: iso(150), lastSeenAt: iso(10), ownerRole: "Backoffice" },
    { sourceModule: "Inventory", causeType: "stockout", effectType: "lost_sale_risk", actionTarget: "Reorder SKU", weight: 26, severity: "CRITICAL", confidence: 58, evidenceCount: 2, incidentIds: ["inc_inv_stockout"], firstSeenAt: iso(90), lastSeenAt: iso(8), ownerRole: "Inventory" },
    { sourceModule: "POS", causeType: "offline_mode", effectType: "pending_evidence", actionTarget: "Keep tablet selling", weight: 14, severity: "INFO", confidence: 78, evidenceCount: 5, incidentIds: ["inc_pos_offline"], firstSeenAt: iso(80), lastSeenAt: iso(3), ownerRole: "Operator" }
  ],
  operationalDensityField: operationalDensityFieldMock,
  operationalDensityHeatmap: operationalDensityHeatmapMock,
  serviceDependencyGraph: {
    nodes: [
      { id: "tablet-3120", label: "Tablet 3120", kind: "app", status: "PASS", port: 3120, localUrl: "local-origin-redacted:3120", healthy: true, criticality: "high", owner: "Operator", lastProbeAt: iso(4) },
      { id: "pc-3130", label: "PC 3130", kind: "app", status: "PASS", port: 3130, localUrl: "local-origin-redacted:3130", healthy: true, criticality: "high", owner: "Backoffice", lastProbeAt: iso(4) },
      { id: "mobile-3140", label: "Mobile 3140", kind: "app", status: "DEGRADED", port: 3140, localUrl: "local-origin-redacted:3140", healthy: true, criticality: "medium", owner: "Owner", lastProbeAt: iso(8) },
      { id: "control-3150", label: "Control 3150", kind: "service", status: "DEGRADED", port: 3150, localUrl: "local-origin-redacted:3150", healthy: false, criticality: "high", owner: "Audit", lastProbeAt: iso(16) },
      { id: "canonical-db", label: "Canonical DB", kind: "db", status: "PASS", healthy: true, criticality: "high", owner: "Prisma ORM", lastProbeAt: iso(6) },
      { id: "cloudflare", label: "Cloudflare", kind: "cloudflare", status: "DEGRADED", publicUrl: "https://control.hitechrts.com", healthy: false, criticality: "medium", owner: "Infra", lastProbeAt: iso(12) }
    ],
    edges: [
      { source: "tablet-3120", target: "pc-3130", relation: "syncs_with", status: "PASS", latencyMs: 96, evidence: "event outbox" },
      { source: "pc-3130", target: "canonical-db", relation: "writes_to", status: "PASS", latencyMs: 38, evidence: "Prisma projector" },
      { source: "mobile-3140", target: "pc-3130", relation: "depends_on", status: "DEGRADED", latencyMs: 142, evidence: "snapshot partial" },
      { source: "control-3150", target: "tablet-3120", relation: "probes", status: "PASS", latencyMs: 64, evidence: "local health" },
      { source: "cloudflare", target: "control-3150", relation: "routes_to", status: "DEGRADED", latencyMs: 410, evidence: "public route probe" }
    ]
  },
  inventoryRiskTreemap: [
    { id: "cat-food", label: "Alimentos", level: "category", stockOnHand: 420, reorderPoint: 160, daysOfCover: 4, velocityPerDay: 92, stockoutRisk: 68, overstockRisk: 8, marginImpact: 142000, revenueAtRisk: 318000, confidence: 45 },
    { id: "sku-pap-ado", parentId: "cat-food", label: "PAP-ADOBO", level: "sku", stockOnHand: 18, reorderPoint: 40, daysOfCover: 1, velocityPerDay: 22, stockoutRisk: 91, overstockRisk: 2, marginImpact: 52000, revenueAtRisk: 126000, confidence: 38 },
    { id: "sku-cho-clas", parentId: "cat-food", label: "CHO-CLAS", level: "sku", stockOnHand: 41, reorderPoint: 55, daysOfCover: 2, velocityPerDay: 21, stockoutRisk: 74, overstockRisk: 4, marginImpact: 42000, revenueAtRisk: 88000, confidence: 42 },
    { id: "cat-drinks", label: "Bebidas", level: "category", stockOnHand: 310, reorderPoint: 120, daysOfCover: 6, velocityPerDay: 44, stockoutRisk: 38, overstockRisk: 16, marginImpact: 62000, revenueAtRisk: 138000, confidence: 50 },
    { id: "sku-ref-355", parentId: "cat-drinks", label: "REF-355ML", level: "sku", stockOnHand: 29, reorderPoint: 44, daysOfCover: 3, velocityPerDay: 16, stockoutRisk: 66, overstockRisk: 6, marginImpact: 24000, revenueAtRisk: 48000, confidence: 44 }
  ],
  decisionLedgerTimeline: [
    { decisionId: "dec-001", time: iso(300), title: "Control route degraded", type: "incident", actorName: "Control", responsibleRole: "Infra", status: "open", relatedIncidentIds: ["inc_cf_404"], evidenceCount: 3, impactScore: 76, beforeHealthScore: 92, afterHealthScore: 84, confidence: 64 },
    { decisionId: "dec-002", time: iso(210), title: "Keep Tablet offline sales open", type: "decision", actorName: "Backoffice", responsibleRole: "Operator", status: "resolved", relatedIncidentIds: ["inc_pos_offline"], evidenceCount: 5, impactScore: 44, beforeHealthScore: 84, afterHealthScore: 87, confidence: 78 },
    { decisionId: "dec-003", time: iso(120), title: "Reorder high-risk SKU", type: "action", actorName: "Inventory", responsibleRole: "Inventory", status: "in_progress", relatedIncidentIds: ["inc_inv_stockout"], evidenceCount: 2, impactScore: 68, beforeHealthScore: 87, afterHealthScore: 88, confidence: 46 },
    { decisionId: "dec-004", time: iso(45), title: "Sync retry review", type: "evidence", actorName: "PC", responsibleRole: "Backoffice", status: "open", relatedIncidentIds: ["inc_sync_retry"], evidenceCount: 4, impactScore: 57, beforeHealthScore: 88, afterHealthScore: 86, confidence: 54 }
  ],
  financialOperationalWaterfall: [
    { id: "gross-sales", label: "Ventas", kind: "positive", value: 482000, currency: "MXN", source: "sales", relatedIds: ["sale_batch"], confidence: 50 },
    { id: "refunds", label: "Devoluciones", kind: "negative", value: -36000, currency: "MXN", source: "refunds", relatedIds: ["return_batch"], confidence: 47 },
    { id: "discounts", label: "Descuentos", kind: "negative", value: -19000, currency: "MXN", source: "discounts", relatedIds: ["discount_batch"], confidence: 42 },
    { id: "shrink", label: "Merma", kind: "negative", value: -27000, currency: "MXN", source: "inventory", relatedIds: ["stock_adj"], confidence: 34 },
    { id: "incidents", label: "Impacto operativo", kind: "negative", value: -42000, currency: "MXN", source: "incidents", relatedIds: ["inc_cf_404", "inc_sync_retry"], confidence: 30 },
    { id: "net", label: "Neto operativo", kind: "subtotal", value: 358000, currency: "MXN", source: "sales", relatedIds: ["calc_net"], confidence: 44 }
  ]
};

export const mockTabletCharts: PrismaTabletChartsViewModel = {
  shiftPulseStrip: [300, 255, 210, 165, 120, 75, 30].map((minutes, index) => ({
    bucketStart: iso(minutes),
    bucketEnd: iso(minutes - 30),
    shiftId: "shift-current",
    terminalId: "terminal_tablet_01",
    cashierId: "cashier_01",
    saleCount: [8, 11, 14, 19, 16, 13, 9][index],
    grossSales: [13800, 18400, 22900, 31800, 27200, 21800, 15100][index],
    refundCount: index === 3 ? 1 : 0,
    cancellationCount: index === 4 ? 1 : 0,
    avgTicket: [1725, 1672, 1635, 1673, 1700, 1676, 1677][index],
    offlineSaleCount: index > 3 ? 2 : 0,
    pendingSyncCount: index > 4 ? 5 : index,
    queuePressure: [22, 28, 36, 64, 58, 42, 30][index],
    status: index === 3 ? "busy" : index === 5 ? "risk" : "normal"
  })),
  syncOutboxStatusMatrix: [
    { itemType: "sale", syncState: "pending", count: 8, oldestAgeMinutes: 14, retryCount: 0, blocking: false, confidence: 70 },
    { itemType: "sale", syncState: "sent", count: 23, oldestAgeMinutes: 2, retryCount: 0, blocking: false, confidence: 78 },
    { itemType: "refund", syncState: "failed", count: 1, oldestAgeMinutes: 44, lastAttemptAt: iso(12), retryCount: 3, blocking: true, confidence: 62 },
    { itemType: "inventory_adjustment", syncState: "retrying", count: 2, oldestAgeMinutes: 31, lastAttemptAt: iso(8), retryCount: 2, blocking: false, confidence: 61 },
    { itemType: "cash_shift", syncState: "pending", count: 1, oldestAgeMinutes: 18, retryCount: 0, blocking: false, confidence: 72 },
    { itemType: "ticket", syncState: "sent", count: 16, oldestAgeMinutes: 3, retryCount: 0, blocking: false, confidence: 76 },
    { itemType: "customer", syncState: "sending", count: 3, oldestAgeMinutes: 5, retryCount: 1, blocking: false, confidence: 66 }
  ]
};

export const mockMobileCharts: PrismaMobileChartsViewModel = {
  ownerPulseTimeline: [360, 300, 240, 180, 120, 60, 0].map((minutes, index) => ({
    time: iso(minutes),
    healthScore: [91, 89, 84, 86, 82, 88, 87][index],
    status: index === 4 ? "DEGRADED" : "PASS",
    activeIncidentCount: [1, 1, 2, 2, 3, 2, 2][index],
    openActionCount: [3, 4, 5, 5, 6, 5, 4][index],
    dataConfidence: [68, 64, 58, 60, 52, 57, 61][index],
    freshnessMinutes: [4, 8, 14, 18, 27, 15, 10][index],
    annotation: index === 4 ? "sync stale" : undefined
  })),
  actionInboxPriorityStack: [
    { responsibleId: "infra", responsibleName: "Infra", role: "Infra", moduleId: "cloudflare", priority: "critical", openCount: 2, overdueCount: 1, blockedCount: 1, dueSoonCount: 1, evidenceMissingCount: 1 },
    { responsibleId: "inventory", responsibleName: "Inventario", role: "Inventario", moduleId: "inventory", priority: "high", openCount: 4, overdueCount: 1, blockedCount: 0, dueSoonCount: 2, evidenceMissingCount: 2 },
    { responsibleId: "backoffice", responsibleName: "Backoffice", role: "PC", moduleId: "sync", priority: "medium", openCount: 3, overdueCount: 0, blockedCount: 0, dueSoonCount: 2, evidenceMissingCount: 1 },
    { responsibleId: "operator", responsibleName: "Operador", role: "Tablet", moduleId: "pos", priority: "low", openCount: 2, overdueCount: 0, blockedCount: 0, dueSoonCount: 1, evidenceMissingCount: 0 }
  ],
  healthRadarCompact: [
    { axis: "data_quality", label: "Calidad", value: 62, status: "DEGRADED", confidence: 58, staleMinutes: 16, topReason: "snapshot partial" },
    { axis: "sync", label: "Sync", value: 55, status: "DEGRADED", confidence: 54, staleMinutes: 23, topReason: "outbox pending" },
    { axis: "alerts", label: "Alertas", value: 71, status: "PASS", confidence: 62, staleMinutes: 8, topReason: "deduped" },
    { axis: "inventory", label: "Inventario", value: 49, status: "DEGRADED", confidence: 44, staleMinutes: 35, topReason: "low stock" },
    { axis: "uptime", label: "Uptime", value: 83, status: "PASS", confidence: 72, staleMinutes: 5, topReason: "local origins ok" },
    { axis: "cashflow", label: "Caja", value: 66, status: "DEGRADED", confidence: 48, staleMinutes: 21, topReason: "mock fallback" }
  ],
  freshnessBeaconGrid: [
    { moduleId: "tablet", moduleName: "Tablet", lastUpdatedAt: iso(4), staleMinutes: 4, ttlMinutes: 15, freshnessState: "fresh", confidence: 74, source: "local" },
    { moduleId: "pc", moduleName: "PC", lastUpdatedAt: iso(18), staleMinutes: 18, ttlMinutes: 15, freshnessState: "aging", confidence: 58, source: "server" },
    { moduleId: "mobile", moduleName: "Mobile", lastUpdatedAt: iso(11), staleMinutes: 11, ttlMinutes: 15, freshnessState: "fresh", confidence: 64, source: "cache" },
    { moduleId: "control", moduleName: "Control", lastUpdatedAt: iso(31), staleMinutes: 31, ttlMinutes: 20, freshnessState: "stale", confidence: 43, source: "public_sanitized" },
    { moduleId: "inventory", moduleName: "Inventario", lastUpdatedAt: iso(55), staleMinutes: 55, ttlMinutes: 30, freshnessState: "stale", confidence: 35, source: "mock" }
  ],
  incidentSparkCards: [
    { incidentId: "inc_cf_404", title: "Control public route degraded", severity: "ERROR", state: "active", moduleId: "cloudflare", points: [80, 72, 84, 76, 68].map((impact, index) => ({ time: iso(120 - index * 20), impactScore: impact, latencyMs: 360 + index * 20 })), recommendedNextAction: "Review DNS/config binding", owner: "Infra", evidenceCount: 4 },
    { incidentId: "inc_sync_retry", title: "Outbox retry pressure", severity: "WARN", state: "recurring", moduleId: "sync", points: [44, 52, 61, 56, 49].map((impact, index) => ({ time: iso(100 - index * 18), impactScore: impact, retryCount: index + 1 })), recommendedNextAction: "Review PC ingest queue", owner: "Backoffice", evidenceCount: 3 },
    { incidentId: "inc_inv_stockout", title: "High velocity SKU risk", severity: "CRITICAL", state: "active", moduleId: "inventory", points: [61, 68, 72, 79, 86].map((impact, index) => ({ time: iso(95 - index * 16), impactScore: impact, healthScore: 88 - index })), recommendedNextAction: "Reorder affected SKU", owner: "Inventory", evidenceCount: 2 }
  ],
  confidenceMeterBands: [
    { dimension: "completeness", label: "Completitud", value: 72, state: "medium", reason: "PC and Tablet available, Control partial", affectedModules: ["control"] },
    { dimension: "recency", label: "Recencia", value: 58, state: "medium", reason: "Some snapshots older than TTL", affectedModules: ["pc", "inventory"] },
    { dimension: "consistency", label: "Consistencia", value: 64, state: "medium", reason: "No conflicting status, but sync is partial", affectedModules: ["sync"] },
    { dimension: "evidence", label: "Evidencia", value: 48, state: "low", reason: "Some high priority actions lack evidence", affectedModules: ["actions", "incidents"] },
    { dimension: "coverage", label: "Cobertura", value: 69, state: "medium", reason: "Business sources still on mock fallback", affectedModules: ["cashflow", "inventory"] }
  ]
};
