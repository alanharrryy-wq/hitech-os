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
  ServiceDependencyEdge,
  ServiceDependencyNode,
  ShiftPulseBucket,
  SyncOutboxMatrixCell
} from "./prismaChartContracts";
import { formatAgeMinutes, formatCurrencyFromCents, formatPercent, humanizeKey } from "./prismaChartFormatters";
import { basePrismaChartOption, severityColor, statusColor } from "./prismaChartTheme";

type ChartOption = Record<string, unknown>;

function timeLabel(iso: string) {
  return new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit" }).format(new Date(iso));
}

function mergeBase(title: string, description: string, option: ChartOption): ChartOption {
  return { ...basePrismaChartOption(title, description), ...option };
}

export function causalFlowRibbonOption(data: CausalFlowRibbonDatum[]): ChartOption {
  const nodes = Array.from(new Set(data.flatMap((item) => [item.sourceModule, item.causeType, item.effectType, item.actionTarget]))).map((name) => ({ name }));
  const links = data.flatMap((item) => [
    { source: item.sourceModule, target: item.causeType, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.46 }, item },
    { source: item.causeType, target: item.effectType, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.38 }, item },
    { source: item.effectType, target: item.actionTarget, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.34 }, item }
  ]);
  return mergeBase("Causal Flow Ribbon", "Sankey ribbon linking source module, cause, effect, and action target.", {
    tooltip: { trigger: "item", formatter: (params: any) => params.data?.item ? `${params.data.item.sourceModule}<br/>${params.data.item.causeType} -> ${params.data.item.effectType}<br/>Action: ${params.data.item.actionTarget}<br/>Evidence: ${params.data.item.evidenceCount}<br/>Confidence: ${formatPercent(params.data.item.confidence)}` : params.name },
    series: [{ type: "sankey", emphasis: { focus: "adjacency" }, nodeWidth: 14, nodeGap: 12, layoutIterations: 32, data: nodes, links, label: { color: "#071426", fontWeight: 800 }, lineStyle: { curveness: 0.55 } }]
  });
}

export function operationalDensityFieldOption(data: OperationalDensityCell[]): ChartOption {
  const modules = Array.from(new Set(data.map((item) => item.moduleName)));
  const buckets = Array.from(new Set(data.map((item) => timeLabel(item.bucketStart))));
  const values = data.map((item) => [buckets.indexOf(timeLabel(item.bucketStart)), modules.indexOf(item.moduleName), item.pressureScore, item]);
  return mergeBase("Operational Density Field", "Heatmap of operational pressure by module and time bucket.", {
    grid: { top: 18, left: 86, right: 22, bottom: 42 },
    xAxis: { type: "category", data: buckets, axisLabel: { color: "#66738a" } },
    yAxis: { type: "category", data: modules, axisLabel: { color: "#071426", fontWeight: 800 } },
    visualMap: { min: 0, max: 100, orient: "horizontal", left: "center", bottom: 0, inRange: { color: ["#eaf2ff", "#63dfff", "#086dff", "#e59b2a", "#df3d2f"] } },
    tooltip: { formatter: (params: any) => `${params.data[3].moduleName}<br/>Pressure: ${params.data[2]}<br/>Events: ${params.data[3].eventCount}<br/>Cause: ${params.data[3].dominantCause}` },
    series: [{ type: "heatmap", data: values, progressive: 0, label: { show: true, color: "#071426", fontWeight: 800 }, emphasis: { itemStyle: { borderColor: "#071426", borderWidth: 1 } } }]
  });
}

export function serviceDependencyGraphOption(graph: { nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] }): ChartOption {
  return mergeBase("Service Dependency Graph", "Dependency graph for apps, endpoints, services, and canonical DB.", {
    tooltip: { formatter: (params: any) => params.dataType === "edge" ? `${params.data.source} -> ${params.data.target}<br/>${params.data.relation}<br/>${params.data.status}` : `${params.data.label}<br/>${params.data.kind}<br/>${params.data.status}` },
    series: [{
      type: "graph",
      layout: "force",
      roam: true,
      force: { repulsion: 210, edgeLength: 88 },
      data: graph.nodes.map((node) => ({ ...node, name: node.id, value: node.latencyMs ?? 0, symbolSize: node.criticality === "high" ? 54 : node.criticality === "medium" ? 42 : 34, itemStyle: { color: statusColor(node.status), borderColor: "#fff", borderWidth: 2 }, label: { show: true, formatter: node.label, color: "#071426", fontWeight: 850 } })),
      links: graph.edges.map((edge) => ({ ...edge, lineStyle: { color: statusColor(edge.status), width: edge.status === "FAIL" ? 4 : 2, curveness: 0.18 } })),
      edgeLabel: { show: false },
      emphasis: { focus: "adjacency" }
    }]
  });
}

export function inventoryRiskTreemapOption(data: InventoryRiskNode[]): ChartOption {
  const roots = data.filter((node) => !node.parentId).map((root) => ({
    name: root.label,
    value: root.revenueAtRisk ?? root.marginImpact ?? root.stockoutRisk,
    itemStyle: { color: statusColor(root.stockoutRisk > 75 ? "FAIL" : root.stockoutRisk > 50 ? "DEGRADED" : "PASS") },
    children: data.filter((node) => node.parentId === root.id).map((child) => ({
      name: child.label,
      value: child.revenueAtRisk ?? child.marginImpact ?? child.stockoutRisk,
      itemStyle: { color: statusColor(child.stockoutRisk > 75 ? "FAIL" : child.stockoutRisk > 50 ? "DEGRADED" : "PASS") },
      node: child
    })),
    node: root
  }));
  return mergeBase("Inventory Risk Treemap", "Treemap showing inventory risk, coverage, and revenue at risk.", {
    tooltip: { formatter: (params: any) => `${params.name}<br/>Risk size: ${formatCurrencyFromCents(params.value ?? 0)}<br/>Stockout: ${params.data?.node?.stockoutRisk ?? "--"}<br/>Coverage: ${params.data?.node?.daysOfCover ?? "--"} days` },
    series: [{ type: "treemap", roam: false, breadcrumb: { show: true }, leafDepth: 1, data: roots, label: { color: "#071426", fontWeight: 850 }, upperLabel: { show: true, color: "#071426", fontWeight: 900 }, itemStyle: { borderColor: "rgba(255,255,255,.74)", borderWidth: 2, gapWidth: 4 } }]
  });
}

export function decisionLedgerTimelineOption(data: DecisionLedgerPoint[]): ChartOption {
  return mergeBase("Decision Ledger Timeline", "Auditable timeline for decisions, actions, evidence, incidents, and resolutions.", {
    grid: { top: 20, left: 44, right: 18, bottom: 40 },
    xAxis: { type: "time", axisLabel: { color: "#66738a" } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#66738a" } },
    tooltip: { formatter: (params: any) => `${params.data.title}<br/>${params.data.type} / ${params.data.status}<br/>Impact: ${params.data.impactScore}<br/>Evidence: ${params.data.evidenceCount}` },
    series: [
      { type: "line", data: data.map((point) => [point.time, point.afterHealthScore ?? point.beforeHealthScore ?? point.impactScore]), smooth: true, lineStyle: { color: "#63dfff", width: 2 }, showSymbol: false },
      { type: "scatter", data: data.map((point) => ({ ...point, value: [point.time, point.impactScore], symbolSize: 12 + point.evidenceCount * 3, itemStyle: { color: statusColor(point.status === "blocked" ? "FAIL" : point.status === "resolved" ? "PASS" : "DEGRADED") } })) }
    ]
  });
}

export function financialOperationalWaterfallOption(data: OperationalWaterfallStep[]): ChartOption {
  let running = 0;
  const helper: number[] = [];
  const values: number[] = [];
  for (const step of data) {
    if (step.kind === "subtotal") {
      helper.push(0);
      values.push(step.value);
      running = step.value;
    } else {
      helper.push(step.value >= 0 ? running : running + step.value);
      values.push(Math.abs(step.value));
      running += step.value;
    }
  }
  return mergeBase("Financial / Operational Waterfall", "Waterfall connecting operations with money impact.", {
    grid: { top: 18, left: 74, right: 20, bottom: 56 },
    xAxis: { type: "category", data: data.map((step) => step.label), axisLabel: { rotate: 18, color: "#66738a" } },
    yAxis: { type: "value", axisLabel: { formatter: (value: number) => formatCurrencyFromCents(value), color: "#66738a" } },
    tooltip: { formatter: (params: any) => `${params.name}<br/>${formatCurrencyFromCents(data[params.dataIndex].value)}<br/>Source: ${data[params.dataIndex].source}<br/>Confidence: ${formatPercent(data[params.dataIndex].confidence)}` },
    series: [
      { type: "bar", stack: "total", itemStyle: { color: "transparent" }, emphasis: { itemStyle: { color: "transparent" } }, data: helper },
      { type: "bar", stack: "total", data: values, itemStyle: { color: (params: any) => data[params.dataIndex].kind === "negative" ? "#df3d2f" : data[params.dataIndex].kind === "subtotal" ? "#071426" : "#13b981", borderRadius: [8, 8, 2, 2] }, label: { show: true, position: "top", formatter: (params: any) => formatCurrencyFromCents(data[params.dataIndex].value), color: "#071426", fontWeight: 800 } }
    ]
  });
}

export function shiftPulseStripOption(data: ShiftPulseBucket[]): ChartOption {
  return mergeBase("Shift Pulse Strip", "Compact shift pulse for sales, ticket count, offline sales, and queue pressure.", {
    grid: { top: 14, left: 48, right: 18, bottom: 34 },
    xAxis: { type: "category", data: data.map((bucket) => timeLabel(bucket.bucketStart)), axisLabel: { color: "#d8e1ec" } },
    yAxis: [{ type: "value", axisLabel: { color: "#d8e1ec" } }, { type: "value", show: false }],
    tooltip: { formatter: (params: any) => `${params[0].axisValue}<br/>Tickets: ${data[params[0].dataIndex].saleCount}<br/>Ventas: ${formatCurrencyFromCents(data[params[0].dataIndex].grossSales)}<br/>Offline: ${data[params[0].dataIndex].offlineSaleCount}<br/>Presion: ${data[params[0].dataIndex].queuePressure}` },
    series: [
      { type: "bar", name: "Tickets", data: data.map((bucket) => bucket.saleCount), itemStyle: { color: "#63dfff", borderRadius: [8, 8, 2, 2] } },
      { type: "line", name: "Ventas", yAxisIndex: 1, data: data.map((bucket) => bucket.grossSales), smooth: true, lineStyle: { color: "#e59b2a", width: 3 }, symbolSize: data.map((bucket) => bucket.queuePressure > 55 ? 10 : 6) }
    ]
  });
}

export function syncOutboxMatrixOption(data: SyncOutboxMatrixCell[]): ChartOption {
  const states = ["pending", "sending", "sent", "failed", "retrying"];
  const items = ["event", "sale", "refund", "inventory_adjustment", "cash_shift", "ticket", "customer"];
  const values = data.map((cell) => [states.indexOf(cell.syncState), items.indexOf(cell.itemType), cell.count, cell]);
  return mergeBase("Sync Outbox Status Matrix", "Compact local outbox heatmap for pending, failed, retrying, and sent items.", {
    grid: { top: 14, left: 126, right: 18, bottom: 38 },
    xAxis: { type: "category", data: states.map(humanizeKey), axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "category", data: items.map(humanizeKey), axisLabel: { color: "#f8fafc", fontWeight: 800 } },
    visualMap: { min: 0, max: 24, show: false, inRange: { color: ["#1d3557", "#086dff", "#e59b2a", "#df3d2f"] } },
    tooltip: { formatter: (params: any) => `${humanizeKey(params.data[3].itemType)} / ${params.data[3].syncState}<br/>Count: ${params.data[3].count}<br/>Oldest: ${formatAgeMinutes(params.data[3].oldestAgeMinutes)}<br/>Retries: ${params.data[3].retryCount}<br/>Blocking: ${params.data[3].blocking ? "yes" : "no"}` },
    series: [{ type: "heatmap", data: values, label: { show: true, color: "#fff", fontWeight: 900 }, emphasis: { itemStyle: { borderColor: "#fff", borderWidth: 1 } } }]
  });
}

export function ownerPulseTimelineOption(data: OwnerPulsePoint[]): ChartOption {
  return mergeBase("Owner Pulse Timeline", "Mobile owner pulse showing recent health trend, incidents, and actions.", {
    grid: { top: 12, left: 38, right: 12, bottom: 32 },
    xAxis: { type: "category", data: data.map((point) => timeLabel(point.time)), axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#d8e1ec" } },
    tooltip: { formatter: (params: any) => `${params.name}<br/>Health: ${params.value}<br/>Incidents: ${data[params.dataIndex].activeIncidentCount}<br/>Actions: ${data[params.dataIndex].openActionCount}<br/>Confidence: ${formatPercent(data[params.dataIndex].dataConfidence)}` },
    series: [
      { type: "line", data: data.map((point) => point.healthScore), smooth: true, symbolSize: 7, lineStyle: { color: "#63dfff", width: 3 }, areaStyle: { color: "rgba(99,223,255,.12)" } },
      { type: "scatter", data: data.map((point, index) => ({ value: point.healthScore, name: timeLabel(point.time), itemStyle: { color: statusColor(point.status) }, symbolSize: 7 + point.activeIncidentCount * 2, dataIndex: index })) }
    ]
  });
}

export function actionInboxPriorityStackOption(data: ActionPriorityStackDatum[]): ChartOption {
  const owners = data.map((item) => item.responsibleName);
  return mergeBase("Action Inbox Priority Stack", "Stacked owner action load by priority, overdue, blocked, and evidence gaps.", {
    grid: { top: 12, left: 88, right: 16, bottom: 28 },
    xAxis: { type: "value", axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "category", data: owners, axisLabel: { color: "#f8fafc", fontWeight: 800 } },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { bottom: 0, textStyle: { color: "#d8e1ec" } },
    series: [
      { type: "bar", name: "Abiertas", stack: "actions", data: data.map((item) => item.openCount), itemStyle: { color: "#63dfff" } },
      { type: "bar", name: "Vencidas", stack: "actions", data: data.map((item) => item.overdueCount), itemStyle: { color: "#e59b2a" } },
      { type: "bar", name: "Bloqueadas", stack: "actions", data: data.map((item) => item.blockedCount), itemStyle: { color: "#df3d2f" } },
      { type: "bar", name: "Sin evidencia", stack: "actions", data: data.map((item) => item.evidenceMissingCount), itemStyle: { color: "#7557ff" } }
    ]
  });
}

export function healthRadarCompactOption(data: HealthRadarAxis[]): ChartOption {
  return mergeBase("Health Radar Compact", "Compact multidimensional health radar for owner supervision.", {
    radar: { radius: "64%", indicator: data.map((axis) => ({ name: axis.label, max: 100 })), axisName: { color: "#f8fafc", fontWeight: 800 }, splitLine: { lineStyle: { color: "rgba(255,255,255,.16)" } }, splitArea: { areaStyle: { color: ["rgba(255,255,255,.04)", "rgba(99,223,255,.05)"] } } },
    tooltip: { formatter: () => data.map((axis) => `${axis.label}: ${axis.value} (${axis.topReason ?? "sin razon"})`).join("<br/>") },
    series: [{ type: "radar", data: [{ value: data.map((axis) => axis.value), name: "Health", areaStyle: { color: "rgba(99,223,255,.18)" }, lineStyle: { color: "#63dfff", width: 3 }, itemStyle: { color: "#e59b2a" } }] }]
  });
}

export function freshnessBeaconGridOption(data: FreshnessBeacon[]): ChartOption {
  const freshnessScore = (item: FreshnessBeacon) => Math.max(0, Math.min(100, Math.round(100 - (item.staleMinutes / Math.max(1, item.ttlMinutes * 2)) * 100)));
  return mergeBase("Freshness Beacon Grid", "Pictorial freshness beacons by module, source, TTL, and confidence.", {
    grid: { top: 14, left: 32, right: 12, bottom: 42 },
    xAxis: { type: "category", data: data.map((item) => item.moduleName), axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#d8e1ec" } },
    tooltip: { formatter: (params: any) => `${data[params.dataIndex].moduleName}<br/>${data[params.dataIndex].freshnessState}<br/>Age: ${formatAgeMinutes(data[params.dataIndex].staleMinutes)}<br/>Source: ${data[params.dataIndex].source}<br/>Confidence: ${formatPercent(data[params.dataIndex].confidence)}` },
    series: [{ type: "pictorialBar", symbol: "roundRect", symbolRepeat: true, symbolSize: [22, 10], symbolMargin: 2, data: data.map((item) => ({ value: freshnessScore(item), itemStyle: { color: statusColor(item.freshnessState) } })) }]
  });
}

export function incidentSparkOption(card: IncidentSparkCard): ChartOption {
  return mergeBase(card.title, `Sparkline for incident ${card.incidentId}.`, {
    grid: { top: 8, left: 8, right: 8, bottom: 8 },
    xAxis: { type: "category", show: false, data: card.points.map((point) => timeLabel(point.time)) },
    yAxis: { type: "value", show: false, min: 0, max: 100 },
    tooltip: { formatter: (params: any) => `${card.title}<br/>Impact: ${params.value}<br/>Action: ${card.recommendedNextAction}` },
    series: [{ type: "line", data: card.points.map((point) => point.impactScore), smooth: true, symbol: "none", lineStyle: { color: severityColor(card.severity), width: 3 }, areaStyle: { color: "rgba(99,223,255,.10)" } }]
  });
}

export function confidenceMeterBandsOption(data: ConfidenceBand[]): ChartOption {
  return mergeBase("Confidence Meter Bands", "Linear confidence bands explaining why the mobile snapshot can or cannot be trusted.", {
    grid: { top: 12, left: 94, right: 18, bottom: 28 },
    xAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "category", data: data.map((item) => item.label), axisLabel: { color: "#f8fafc", fontWeight: 800 } },
    tooltip: { formatter: (params: any) => `${data[params.dataIndex].label}<br/>${params.value}<br/>${data[params.dataIndex].reason}<br/>Modules: ${data[params.dataIndex].affectedModules.join(", ")}` },
    series: [{ type: "bar", data: data.map((item) => ({ value: item.value, itemStyle: { color: statusColor(item.state), borderRadius: [0, 999, 999, 0] } })), label: { show: true, position: "right", formatter: (params: any) => formatPercent(params.value), color: "#f8fafc", fontWeight: 900 } }]
  });
}
