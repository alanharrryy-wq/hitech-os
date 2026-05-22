import type { PrismaChartDefinition, PrismaChartFilter, PrismaChartInteraction, PrismaChartSurface } from "./prismaChartContracts";

const pcFilters: PrismaChartFilter[] = [
  { id: "time", label: "Tiempo", values: ["1h", "24h", "7d", "custom"] },
  { id: "severity", label: "Severidad", values: ["WARN", "ERROR", "CRITICAL"] },
  { id: "module", label: "Modulo", values: ["Cloudflare", "Sync", "Inventory", "POS", "Workers"] },
  { id: "confidence", label: "Confianza minima", values: [">=50", ">=70", ">=90"] }
];

const tabletFilters: PrismaChartFilter[] = [
  { id: "shift", label: "Turno", values: ["actual", "anterior"] },
  { id: "metric", label: "Metrica", values: ["ventas", "tickets", "promedio", "offline"] },
  { id: "syncState", label: "Estado sync", values: ["pending", "failed", "retrying"] }
];

const mobileFilters: PrismaChartFilter[] = [
  { id: "range", label: "Rango", values: ["24h", "7d", "30d"] },
  { id: "priority", label: "Prioridad", values: ["medium", "high", "critical"] },
  { id: "freshness", label: "Frescura", values: ["solo stale", "baja confianza"] }
];

const pcInteractions: PrismaChartInteraction[] = [
  { event: "hover", label: "Tooltip con dato humano y evidencia", safe: true },
  { event: "click", label: "Foco local de modulo o incidente", safe: true },
  { event: "brush", label: "Seleccion de ventana sin navegar", safe: true },
  { event: "legend", label: "Filtrado visual por estado/severidad", safe: true }
];

const tabletInteractions: PrismaChartInteraction[] = [
  { event: "tap", label: "Tap de celda/bucket para resumen local", safe: true },
  { event: "reset", label: "Reset tactil de filtros", safe: true }
];

const mobileInteractions: PrismaChartInteraction[] = [
  { event: "tap", label: "Expande explicacion o accion recomendada", safe: true },
  { event: "swipe", label: "Navegacion compacta sin rutas faltantes", safe: false },
  { event: "hover", label: "Tooltip accesible en dispositivos compatibles", safe: true }
];

export const prismaChartRegistry: PrismaChartDefinition[] = [
  {
    id: "pc.causal-flow-ribbon",
    surface: "pc",
    title: "Causal Flow Ribbon",
    componentName: "PcCausalFlowRibbon",
    renderer: "canvas",
    echartsSeries: ["sankey"],
    purpose: "Map source module, cause, effect, and action target.",
    visualEncoding: "Ribbon width maps impact, color maps severity, tooltip maps evidence.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "ARIA summary plus text drawer focus label.",
    responsive: "Wide first-row card on desktop, single column below 980px.",
    dataContract: "CausalFlowRibbonDatum[]",
    route: "/prisma-insights"
  },
  {
    id: "pc.operational-density-field",
    surface: "pc",
    title: "Operational Density Field",
    componentName: "PcOperationalDensityField",
    renderer: "canvas",
    echartsSeries: ["heatmap", "visualMap"],
    purpose: "Reveal pressure concentration by module and time.",
    visualEncoding: "X axis time buckets, Y axis modules, color intensity pressure score.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Heatmap cells include module, bucket, pressure, and dominant cause.",
    responsive: "Maintains horizontal scroll-free density with compact labels.",
    dataContract: "OperationalDensityCell[]",
    route: "/prisma-insights"
  },
  {
    id: "ops.operational-density-heatmap",
    surface: "pc",
    title: "Operational Density Heatmap",
    componentName: "OpsOperationalDensityHeatmap",
    renderer: "canvas",
    echartsSeries: ["heatmap", "visualMap"],
    purpose: "Lab-governed operational density heatmap for pressure and anomaly exploration.",
    visualEncoding: "Dense time/module matrix maps pressure, anomaly labels, and evidence callouts.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Heatmap exposes module, bucket, pressure, state, and evidence in tooltip text.",
    responsive: "Lab-first wide heatmap; product promotion requires explicit wrapper.",
    dataContract: "OperationalDensityCell[]",
    route: "/prisma-insights/chart-lab"
  },
  {
    id: "pc.service-dependency-graph",
    surface: "pc",
    title: "Service Dependency Graph",
    componentName: "PcServiceDependencyGraph",
    renderer: "canvas",
    echartsSeries: ["graph"],
    purpose: "Show dependencies between apps, services, endpoints, DB, and Control Center.",
    visualEncoding: "Node size maps criticality, color maps status, edges map relation.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Graph has node count, degraded path notes, and click focus.",
    responsive: "Force graph compacts under narrow widths.",
    dataContract: "{ nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] }",
    route: "/prisma-insights"
  },
  {
    id: "pc.inventory-risk-treemap",
    surface: "pc",
    title: "Inventory Risk Treemap",
    componentName: "PcInventoryRiskTreemap",
    renderer: "canvas",
    echartsSeries: ["treemap"],
    purpose: "Expose inventory money and continuity risk by category/SKU.",
    visualEncoding: "Block area maps revenue risk, color maps stockout risk.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Breadcrumb and tooltip describe category/SKU risk.",
    responsive: "Treemap reflows within a fixed-height governance card.",
    dataContract: "InventoryRiskNode[]",
    route: "/prisma-insights"
  },
  {
    id: "pc.decision-ledger-timeline",
    surface: "pc",
    title: "Decision Ledger Timeline",
    componentName: "PcDecisionLedgerTimeline",
    renderer: "canvas",
    echartsSeries: ["scatter", "line"],
    purpose: "Audit decisions, evidence, incidents, and resolutions over time.",
    visualEncoding: "Time x impact score, symbol size evidence, color status.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Event list is summarized through click focus text.",
    responsive: "Short third-row timeline, compact labels.",
    dataContract: "DecisionLedgerPoint[]",
    route: "/prisma-insights"
  },
  {
    id: "pc.financial-operational-waterfall",
    surface: "pc",
    title: "Financial / Operational Waterfall",
    componentName: "PcFinancialOperationalWaterfall",
    renderer: "canvas",
    echartsSeries: ["bar"],
    purpose: "Connect operating changes to money impact.",
    visualEncoding: "Waterfall bars show positive, negative, subtotal, and neutral steps.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Formula and source per bar in tooltip.",
    responsive: "Bars stay readable with rotated compact labels on small widths.",
    dataContract: "OperationalWaterfallStep[]",
    route: "/prisma-insights"
  },
  {
    id: "pc.tablet-catalog-freshness-grid",
    surface: "pc",
    title: "Tablet Catalog Freshness Grid",
    componentName: "PcSyncChartPromotionPanel",
    renderer: "canvas",
    echartsSeries: ["heatmap"],
    purpose: "Show which Tablets are fresh, stale, conflicted, or missing catalog checkpoints by entity.",
    visualEncoding: "Rows map Tablets, columns map catalog entities, color maps freshness and checkpoint risk.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Each row exposes checkpoint, counts, errors, and recommended action as text.",
    responsive: "Mounted as a compact operational grid inside the PC /sync workflow.",
    dataContract: "TabletCatalogFreshnessGridRow[]",
    route: "/sync"
  },
  {
    id: "pc.sync-command-lifecycle-timeline",
    surface: "pc",
    title: "Sync Command Lifecycle Timeline",
    componentName: "PcSyncChartPromotionPanel",
    renderer: "canvas",
    echartsSeries: ["scatter"],
    purpose: "Trace catalog delta, bootstrap, resync, and runtime refresh lifecycle events.",
    visualEncoding: "Time maps lifecycle order, status lane maps command state, symbol size maps entity volume.",
    filters: pcFilters,
    interactions: pcInteractions,
    accessibility: "Timeline events expose source, terminal, result counts, reason, and recommended action as text.",
    responsive: "Mounted as a compact event lane inside the PC /sync workflow.",
    dataContract: "SyncCommandLifecycleEvent[]",
    route: "/sync"
  },
  {
    id: "tablet.shift-pulse-strip",
    surface: "tablet",
    title: "Shift Pulse Strip",
    componentName: "TabletShiftPulseStrip",
    renderer: "svg",
    echartsSeries: ["line", "bar"],
    purpose: "Answer whether the current shift can keep operating.",
    visualEncoding: "Bars map tickets, line maps gross sales, markers map queue pressure.",
    filters: tabletFilters,
    interactions: tabletInteractions,
    accessibility: "Large touch summary labels and non-color status text.",
    responsive: "180-220px tactical card for tablet touch surfaces.",
    dataContract: "ShiftPulseBucket[]",
    route: "/prisma-pulse"
  },
  {
    id: "tablet.sync-outbox-status-matrix",
    surface: "tablet",
    title: "Sync Outbox Status Matrix",
    componentName: "TabletSyncOutboxStatusMatrix",
    renderer: "svg",
    echartsSeries: ["heatmap"],
    purpose: "Show what is pending, failed, old, or blocking in the local outbox.",
    visualEncoding: "Cell position maps item/status, color maps count and blocking state.",
    filters: tabletFilters,
    interactions: tabletInteractions,
    accessibility: "Cell tooltip includes count, oldest age, retry count, and blocking text.",
    responsive: "Compact matrix with touch-safe cell focus.",
    dataContract: "SyncOutboxMatrixCell[]",
    route: "/prisma-pulse"
  },
  {
    id: "mobile.owner-pulse-timeline",
    surface: "mobile",
    title: "Owner Pulse Timeline",
    componentName: "MobileOwnerPulseTimeline",
    renderer: "svg",
    echartsSeries: ["line", "scatter"],
    purpose: "Show whether the operation is improving or degrading recently.",
    visualEncoding: "Line maps health score, points map incidents and annotations.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Tap point summary with status, incidents, actions, and confidence.",
    responsive: "160-200px command card for small screens.",
    dataContract: "OwnerPulsePoint[]",
    route: "/prisma-command"
  },
  {
    id: "mobile.action-inbox-priority-stack",
    surface: "mobile",
    title: "Action Inbox Priority Stack",
    componentName: "MobileActionInboxPriorityStack",
    renderer: "svg",
    echartsSeries: ["bar"],
    purpose: "Show who owns open actions by priority and module.",
    visualEncoding: "Horizontal stacked bars map priority and overdue/blocked counts.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Bar tooltip exposes owner, role, module, and missing evidence.",
    responsive: "Compact horizontal bars with readable owner labels.",
    dataContract: "ActionPriorityStackDatum[]",
    route: "/prisma-command"
  },
  {
    id: "mobile.health-radar-compact",
    surface: "mobile",
    title: "Health Radar Compact",
    componentName: "MobileHealthRadarCompact",
    renderer: "svg",
    echartsSeries: ["radar"],
    purpose: "Reveal which operating dimension is weak behind the score.",
    visualEncoding: "Radar axes map data quality, sync, alerts, inventory, uptime, cashflow.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Axis tooltip includes score, stale minutes, confidence, and top reason.",
    responsive: "Small radial chart that does not wrap the main score.",
    dataContract: "HealthRadarAxis[]",
    route: "/prisma-command"
  },
  {
    id: "mobile.freshness-beacon-grid",
    surface: "mobile",
    title: "Freshness Rings",
    componentName: "MobileFreshnessRings",
    renderer: "svg",
    echartsSeries: ["pictorialBar"],
    purpose: "Show whether each module's data is fresh, aging, stale, offline, or unknown.",
    visualEncoding: "Beacon height maps freshness, color maps state, label maps source.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Beacon tooltip explains freshness, source, TTL, and confidence.",
    responsive: "Glanceable module beacons in one compact card.",
    dataContract: "FreshnessBeacon[]",
    route: "/prisma-command"
  },
  {
    id: "mobile.incident-spark-cards",
    surface: "mobile",
    title: "Incident Spark Cards",
    componentName: "MobileIncidentSparkCards",
    renderer: "svg",
    echartsSeries: ["line"],
    purpose: "Show active incident microtrends without opening PC.",
    visualEncoding: "Small multiple lines map impact score per incident.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Each card has incident title, owner, next action, evidence count.",
    responsive: "92-120px mini charts stacked on mobile.",
    dataContract: "IncidentSparkCard[]",
    route: "/prisma-command"
  },
  {
    id: "mobile.confidence-meter-bands",
    surface: "mobile",
    title: "Confidence Meter Bands",
    componentName: "MobileConfidenceMeterBands",
    renderer: "svg",
    echartsSeries: ["bar"],
    purpose: "Break snapshot confidence into reasons and affected modules.",
    visualEncoding: "Linear bands map confidence dimensions; no circular score meter.",
    filters: mobileFilters,
    interactions: mobileInteractions,
    accessibility: "Band tooltip explains reason and affected modules.",
    responsive: "Short horizontal bars for one-handed reading.",
    dataContract: "ConfidenceBand[]",
    route: "/prisma-command"
  }
];

export function chartsForSurface(surface: PrismaChartSurface) {
  return prismaChartRegistry.filter((chart) => chart.surface === surface);
}
