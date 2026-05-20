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
type TooltipRecord = Record<string, unknown>;

function timeLabel(iso: string | undefined) {
  const date = new Date(iso ?? "");
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit" }).format(date);
}

function mergeBase(title: string, description: string, option: ChartOption): ChartOption {
  return { ...basePrismaChartOption(title, description), ...option };
}


function asRecord(value: unknown): TooltipRecord | null {
  return value && typeof value === "object" && !Array.isArray(value) ? value as TooltipRecord : null;
}

function firstTooltipParam(params: unknown): TooltipRecord | null {
  return asRecord(Array.isArray(params) ? params[0] : params);
}

function tooltipData(params: unknown) {
  return firstTooltipParam(params)?.data;
}

function tooltipDataArray(params: unknown) {
  const data = tooltipData(params);
  return Array.isArray(data) ? data : [];
}

function tooltipDataRecord(params: unknown) {
  return asRecord(tooltipData(params));
}

function tooltipDataIndex(params: unknown) {
  const dataIndex = firstTooltipParam(params)?.dataIndex;
  return typeof dataIndex === "number" && Number.isInteger(dataIndex) && dataIndex >= 0 ? dataIndex : null;
}

function itemByTooltipIndex<T>(items: T[], params: unknown) {
  const dataIndex = tooltipDataIndex(params);
  return dataIndex !== null && dataIndex < items.length ? items[dataIndex] : undefined;
}

function tooltipLabel(params: unknown) {
  const param = firstTooltipParam(params);
  const value = param?.axisValue ?? param?.name;
  return value === null || value === undefined ? "" : String(value);
}

function safeNumber(value: unknown, fallback = 0) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function densityBucketLabel(item: Pick<OperationalDensityCell, "bucketLabel" | "bucketStart">) {
  return item.bucketLabel ?? timeLabel(item.bucketStart);
}

function densityStateColor(state: OperationalDensityCell["state"] | undefined, pressureScore: number) {
  if (state === "anomaly") return "#ff3d6e";
  if (state === "peak") return "#ffbf4d";
  if (state === "cold") return "#12345e";
  if (pressureScore >= 88) return "#ff4f5e";
  if (pressureScore >= 76) return "#ffbf4d";
  if (pressureScore >= 58) return "#8b5cff";
  if (pressureScore >= 36) return "#1fe7ff";
  return "#0c2f6c";
}

function densityTooltip(item: Partial<OperationalDensityCell> | null | undefined) {
  if (!item) return "";
  const state = item.state ?? "normal";
  const riskLine = item.anomalyLabel ? `<b>${item.anomalyLabel}</b><br/>` : "";
  const pressureScore = safeNumber(item.pressureScore);
  return [
    `<div style="min-width:210px">${riskLine}<b>${item.moduleName ?? "Unknown module"}</b> · ${item.bucketLabel ?? timeLabel(item.bucketStart)}`,
    `Presión: <b>${pressureScore}/100</b> · Estado: <b>${state}</b>`,
    `Eventos: ${safeNumber(item.eventCount)} · Warn: ${safeNumber(item.warnCount)} · Error: ${safeNumber(item.errorCount)}`,
    `Latencia media: ${item.avgLatencyMs ?? "--"}ms · Retry: ${item.retryCount ?? 0}`,
    `Confianza: ${formatPercent(safeNumber(item.confidence))} · Causa: ${item.dominantCause ?? "normal_pressure"}`,
    `Acción: ${item.actionHint ?? "Mantener monitoreo"}`,
    item.evidenceRef ? `Evidencia: ${item.evidenceRef}</div>` : "</div>"
  ].join("<br/>");
}

function densityTooltipFromParams(params: unknown) {
  const dataRecord = tooltipDataRecord(params);
  if (dataRecord?.meta) return densityTooltip(dataRecord.meta as Partial<OperationalDensityCell>);
  const dataArray = tooltipDataArray(params);
  return densityTooltip(asRecord(dataArray[3]) as Partial<OperationalDensityCell> | null) || tooltipLabel(params);
}

export function causalFlowRibbonOption(data: CausalFlowRibbonDatum[] | unknown): ChartOption {
  const rows: CausalFlowRibbonDatum[] = Array.isArray(data)
    ? data
    : Array.isArray((data as { data?: unknown })?.data)
      ? ((data as { data: CausalFlowRibbonDatum[] }).data)
      : Array.isArray((data as { items?: unknown })?.items)
        ? ((data as { items: CausalFlowRibbonDatum[] }).items)
        : [];

  const nodes = Array.from(new Set(rows.flatMap((item) => [item.sourceModule, item.causeType, item.effectType, item.actionTarget]).filter(Boolean))).map((name) => ({ name }));
  const links = rows.flatMap((item) => [
    { source: item.sourceModule, target: item.causeType, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.46 }, item },
    { source: item.causeType, target: item.effectType, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.38 }, item },
    { source: item.effectType, target: item.actionTarget, value: item.weight, lineStyle: { color: severityColor(item.severity), opacity: 0.34 }, item }
  ]);
  return mergeBase("Causal Flow Ribbon", "Sankey ribbon linking source module, cause, effect, and action target.", {
    tooltip: {
      trigger: "item",
      formatter: (params: unknown) => {
        const item = asRecord(tooltipDataRecord(params)?.item) as Partial<CausalFlowRibbonDatum> | null;
        return item
          ? `${item.sourceModule ?? ""}<br/>${item.causeType ?? ""} -> ${item.effectType ?? ""}<br/>Action: ${item.actionTarget ?? ""}<br/>Evidence: ${safeNumber(item.evidenceCount)}<br/>Confidence: ${formatPercent(safeNumber(item.confidence))}`
          : tooltipLabel(params);
      }
    },
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
    tooltip: {
      formatter: (params: unknown) => {
        const tuple = tooltipDataArray(params);
        const item = asRecord(tuple[3]) as Partial<OperationalDensityCell> | null;
        if (!item) return tooltipLabel(params);
        return `${item.moduleName ?? ""}<br/>Pressure: ${safeNumber(tuple[2], safeNumber(item.pressureScore))}<br/>Events: ${safeNumber(item.eventCount)}<br/>Cause: ${item.dominantCause ?? "normal_pressure"}`;
      }
    },
    series: [{ type: "heatmap", data: values, progressive: 0, label: { show: true, color: "#071426", fontWeight: 800 }, emphasis: { itemStyle: { borderColor: "#071426", borderWidth: 1 } } }]
  });
}


export function operationalDensityHeatmapOption(data: OperationalDensityCell[]): ChartOption {
  const modules = Array.from(new Set(data.map((item) => item.moduleName)));
  const buckets = Array.from(new Set(data.map(densityBucketLabel)));
  const majorBuckets = new Set(["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "24:00"]);
  const heatCells = data.map((item) => ({
    value: [buckets.indexOf(densityBucketLabel(item)), modules.indexOf(item.moduleName), item.pressureScore, item.confidence, item.eventCount],
    meta: item,
    itemStyle: {
      borderColor: "rgba(150, 205, 255, 0.16)",
      borderWidth: 0.35,
      opacity: item.state === "gap" ? 0.28 : 0.96
    }
  }));
  return mergeBase("Operational Density Heatmap", "Interactive pixel-field heatmap for operational pressure by module and half-hour, with heat-zone controls, richer thermal palette, and evidence callouts.", {
    backgroundColor: "transparent",
    animationDuration: 780,
    animationEasing: "quarticOut",
    grid: { top: 62, left: 122, right: 34, bottom: 42, containLabel: false },
    title: {
      text: "Operational Density Heatmap",
      subtext: "Módulos × tiempo · presión · anomalías · evidencia",
      left: 18,
      top: 10,
      textStyle: { color: "#eef7ff", fontSize: 15, fontWeight: 900 },
      subtextStyle: { color: "#8fb7d9", fontSize: 11, fontWeight: 700 }
    },
    xAxis: {
      type: "category",
      data: buckets,
      position: "top",
      boundaryGap: true,
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: {
        color: "#dcecff",
        fontWeight: 850,
        fontSize: 10,
        margin: 10,
        formatter: (value: string) => majorBuckets.has(value) ? value : ""
      },
      splitArea: { show: true, areaStyle: { color: ["rgba(255,255,255,.010)", "rgba(58,115,178,.018)"] } },
      splitLine: { show: true, lineStyle: { color: "rgba(150, 198, 244, .10)", width: 0.7 } }
    },
    yAxis: {
      type: "category",
      data: modules,
      inverse: true,
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { color: "#f5f9ff", fontWeight: 900, fontSize: 11, margin: 14 },
      splitArea: { show: true, areaStyle: { color: ["rgba(255,255,255,.008)", "rgba(99,223,255,.014)"] } },
      splitLine: { show: true, lineStyle: { color: "rgba(150, 198, 244, .09)", width: 0.7 } }
    },
    visualMap: {
      show: false,
      type: "continuous",
      min: 0,
      max: 92,
      dimension: 2,
      seriesIndex: 0,
      inRange: { color: ["#051229", "#0b2e72", "#1167dd", "#18d7ff", "#735cff", "#e44bc2", "#ff536d", "#ff9f4d", "#fff0a8"] },
      outOfRange: { color: ["rgba(7,20,38,.35)"] }
    },
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(7, 17, 38, 0.94)",
      borderColor: "rgba(148, 218, 255, 0.58)",
      borderWidth: 1,
      padding: [11, 13],
      textStyle: { color: "#eef7ff", fontSize: 12, fontWeight: 650 },
      extraCssText: "box-shadow:0 18px 60px rgba(0,0,0,.48);backdrop-filter:blur(16px);border-radius:12px;",
      formatter: (params: unknown) => densityTooltipFromParams(params)
    },
    graphic: [
      {
        type: "group",
        left: "48%",
        top: "34%",
        silent: true,
        children: [
          { type: "rect", shape: { width: 154, height: 34, r: 7 }, style: { fill: "rgba(203,237,255,.82)", stroke: "rgba(255,255,255,.80)", lineWidth: 1, shadowBlur: 18, shadowColor: "rgba(99,223,255,.42)" } },
          { type: "text", left: 12, top: 7, style: { text: "Pico de carga\n12:45", fill: "#083154", fontSize: 10, fontWeight: 900, lineHeight: 13 } }
        ]
      },
      {
        type: "group",
        left: "58%",
        top: "66%",
        silent: true,
        children: [
          { type: "rect", shape: { width: 178, height: 36, r: 7 }, style: { fill: "rgba(203,237,255,.78)", stroke: "rgba(255,255,255,.78)", lineWidth: 1, shadowBlur: 18, shadowColor: "rgba(255,79,163,.34)" } },
          { type: "text", left: 12, top: 8, style: { text: "△  Anomalía detectada\n19:32", fill: "#083154", fontSize: 10, fontWeight: 900, lineHeight: 13 } }
        ]
      }
    ],
    series: [
      {
        name: "Densidad operacional",
        type: "heatmap",
        coordinateSystem: "cartesian2d",
        data: heatCells,
        progressive: 0,
        label: { show: false, formatter: () => "" },
        labelLayout: { hideOverlap: true },
        itemStyle: {
          borderColor: "rgba(150, 205, 255, 0.16)",
          borderWidth: 0.35,
          borderRadius: 0,
          shadowBlur: 0,
          shadowColor: "rgba(31, 231, 255, 0.08)"
        },
        emphasis: {
          focus: "self",
          itemStyle: { borderColor: "rgba(255,255,255,.82)", borderWidth: 1.05, shadowBlur: 12, shadowColor: "rgba(99,223,255,.42)" },
          label: { show: false, formatter: () => "" }
        },
        blur: { label: { show: false } },
        select: { label: { show: false } }
      }
    ]
  });
}


export function serviceDependencyGraphOption(graph: { nodes: ServiceDependencyNode[]; edges: ServiceDependencyEdge[] }): ChartOption {
  return mergeBase("Service Dependency Graph", "Dependency graph for apps, endpoints, services, and canonical DB.", {
    tooltip: {
      formatter: (params: unknown) => {
        const param = firstTooltipParam(params);
        const item = tooltipDataRecord(params);
        if (!item) return tooltipLabel(params);
        return param?.dataType === "edge"
          ? `${item.source ?? ""} -> ${item.target ?? ""}<br/>${item.relation ?? ""}<br/>${item.status ?? ""}`
          : `${item.label ?? item.name ?? ""}<br/>${item.kind ?? ""}<br/>${item.status ?? ""}`;
      }
    },
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
    tooltip: {
      formatter: (params: unknown) => {
        const item = tooltipDataRecord(params);
        const node = asRecord(item?.node);
        return `${tooltipLabel(params)}<br/>Risk size: ${formatCurrencyFromCents(safeNumber(firstTooltipParam(params)?.value))}<br/>Stockout: ${node?.stockoutRisk ?? "--"}<br/>Coverage: ${node?.daysOfCover ?? "--"} days`;
      }
    },
    series: [{ type: "treemap", roam: false, breadcrumb: { show: true }, leafDepth: 1, data: roots, label: { color: "#071426", fontWeight: 850 }, upperLabel: { show: true, color: "#071426", fontWeight: 900 }, itemStyle: { borderColor: "rgba(255,255,255,.74)", borderWidth: 2, gapWidth: 4 } }]
  });
}

// PRISMA_DECISION_LEDGER_RADICAL_BASELINE_V1
export function decisionLedgerTimelineOption(data: DecisionLedgerPoint[]): ChartOption {
  // PRISMA_DECISION_LEDGER_EXECUTIVE_OPTION_V1: refined, control-safe timeline option.
  const healthSeries = data.map((point) => [point.time, point.afterHealthScore ?? point.beforeHealthScore ?? point.impactScore]);
  const eventItems = data.map((point) => {
    const eventTone = point.status === "blocked" ? "FAIL" : point.status === "resolved" ? "PASS" : "DEGRADED";
    const eventColor = statusColor(eventTone);
    const symbol = point.type === "incident" ? "path://M12 2L22 20H2L12 2Z" : point.type === "decision" ? "diamond" : point.type === "action" ? "roundRect" : point.type === "resolution" ? "pin" : "circle";
    return {
      ...point,
      value: [point.time, point.impactScore],
      symbol,
      symbolSize: Math.max(18, Math.min(34, 14 + point.evidenceCount * 3 + Math.round(point.confidence / 14))),
      itemStyle: {
        color: eventColor,
        borderColor: "rgba(255, 255, 255, 0.96)",
        borderWidth: 2,
        shadowColor: eventColor,
        shadowBlur: point.status === "resolved" ? 12 : 22
      }
    };
  });
  const pulseItems = eventItems.filter((point) => point.status !== "resolved");

  return mergeBase("Decision Ledger Timeline", "Auditable timeline for decisions, actions, evidence, incidents, and resolutions.", {
    backgroundColor: "transparent",
    animation: true,
    animationDuration: 980,
    animationDurationUpdate: 620,
    animationEasing: "cubicOut",
    animationEasingUpdate: "quarticOut",
    title: {
      show: true,
      left: 14,
      top: 8,
      text: "Decision Ledger Timeline",
      subtext: "Evidence-backed governance events over operational health",
      textStyle: { color: "#071426", fontSize: 14, fontWeight: 900 },
      subtextStyle: { color: "#66738a", fontSize: 10, fontWeight: 700 }
    },
    grid: { top: 76, left: 46, right: 22, bottom: 46, containLabel: true },
    legend: {
      show: true,
      top: 42,
      left: 14,
      itemWidth: 10,
      itemHeight: 10,
      icon: "roundRect",
      textStyle: { color: "#66738a", fontSize: 10, fontWeight: 800 },
      data: ["Health score", "Ledger events", "Event pulse"]
    },
    dataZoom: [
      { type: "inside", xAxisIndex: 0, filterMode: "none", zoomOnMouseWheel: true, moveOnMouseMove: true },
      {
        type: "slider",
        xAxisIndex: 0,
        height: 16,
        bottom: 14,
        borderColor: "rgba(99, 223, 255, 0.22)",
        backgroundColor: "rgba(255, 255, 255, 0.42)",
        fillerColor: "rgba(8, 109, 255, 0.15)",
        handleStyle: { color: "#ffffff", borderColor: "#086dff", shadowBlur: 10, shadowColor: "rgba(8, 109, 255, 0.22)" },
        textStyle: { color: "#66738a", fontWeight: 750 },
        brushSelect: true
      }
    ],
    axisPointer: {
      show: true,
      triggerTooltip: true,
      label: { show: true, backgroundColor: "rgba(7, 20, 38, 0.86)", color: "#ffffff", fontWeight: 800 },
      lineStyle: { color: "rgba(8, 109, 255, 0.34)", width: 1, type: "dashed" }
    },
    xAxis: {
      type: "time",
      boundaryGap: false,
      axisLine: { lineStyle: { color: "rgba(112, 144, 176, 0.28)" } },
      axisTick: { show: false },
      splitLine: { show: true, lineStyle: { color: "rgba(112, 144, 176, 0.15)", type: "dashed" } },
      axisLabel: { color: "#66738a", fontSize: 10, fontWeight: 750 }
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      name: "Health / impact",
      nameTextStyle: { color: "#66738a", fontSize: 10, fontWeight: 900, align: "left" },
      axisLine: { show: false },
      axisTick: { show: false },
      splitNumber: 4,
      splitLine: { lineStyle: { color: "rgba(112, 144, 176, 0.15)", type: "dashed" } },
      axisLabel: { color: "#66738a", fontSize: 10, fontWeight: 750 }
    },
    tooltip: {
      show: true,
      trigger: "item",
      confine: true,
      enterable: true,
      borderWidth: 1,
      borderColor: "rgba(99, 223, 255, 0.34)",
      backgroundColor: "rgba(255, 255, 255, 0.94)",
      extraCssText: "border-radius:16px;box-shadow:0 22px 70px rgba(7,20,38,.16);backdrop-filter:blur(18px);",
      textStyle: { color: "#071426" },
      formatter: (params: any) => {
        const item = params.data;
        if (!item || !item.decisionId) return `Health score<br/><b>${Array.isArray(params.value) ? params.value[1] : params.value}</b>/100`;
        return `<b>${item.title}</b><br/>${item.type} / ${item.status}<br/>Actor: ${item.actorName}<br/>Responsible: ${item.responsibleRole}<br/>Impact: ${item.impactScore}/100<br/>Confidence: ${formatPercent(item.confidence)}<br/>Evidence: ${item.evidenceCount}<br/>Health: ${item.beforeHealthScore ?? "--"} -> ${item.afterHealthScore ?? "--"}`;
      }
    },
    series: [
      {
        name: "Health score",
        type: "line",
        data: healthSeries,
        smooth: 0.42,
        symbol: "circle",
        symbolSize: 6,
        showSymbol: false,
        sampling: "lttb",
        z: 4,
        lineStyle: { color: "#63dfff", width: 3, shadowBlur: 14, shadowColor: "rgba(99, 223, 255, 0.44)" },
        areaStyle: { color: "rgba(99, 223, 255, 0.13)" },
        markLine: {
          silent: true,
          symbol: "none",
          label: { formatter: "Target 90", color: "#13b981", fontWeight: 900, fontSize: 10, position: "insideEndTop" },
          lineStyle: { color: "rgba(19, 185, 129, 0.42)", type: "dashed", width: 1.5 },
          data: [{ yAxis: 90 }]
        },
        markArea: {
          silent: true,
          itemStyle: { color: "rgba(229, 155, 42, 0.065)" },
          data: pulseItems.map((point) => [{ xAxis: point.time }, { xAxis: point.time }])
        }
      },
      {
        name: "Ledger events",
        type: "scatter",
        data: eventItems,
        z: 7,
        labelLayout: { hideOverlap: true, moveOverlap: "shiftY" },
        label: {
          show: true,
          position: "top",
          distance: 10,
          color: "#071426",
          fontSize: 10,
          fontWeight: 900,
          formatter: (params: any) => params.data?.title ?? "",
          backgroundColor: "rgba(255, 255, 255, 0.74)",
          borderColor: "rgba(99, 223, 255, 0.18)",
          borderWidth: 1,
          borderRadius: 9,
          padding: [4, 7]
        },
        emphasis: { scale: 1.24, focus: "self", itemStyle: { shadowBlur: 34, borderWidth: 3 }, label: { show: true } },
        select: { itemStyle: { borderWidth: 4, shadowBlur: 40, shadowColor: "rgba(8, 109, 255, 0.38)" }, label: { show: true, backgroundColor: "rgba(7, 20, 38, 0.9)", color: "#ffffff" } },
        selectedMode: "single"
      },
      {
        name: "Event pulse",
        type: "effectScatter",
        data: pulseItems,
        z: 6,
        symbol: "circle",
        symbolSize: 34,
        rippleEffect: { number: 3, scale: 2.5, brushType: "stroke" },
        itemStyle: { color: "#63dfff", opacity: 0.22, shadowBlur: 24, shadowColor: "rgba(99, 223, 255, 0.34)" },
        tooltip: { show: false },
        label: { show: false }
      }
    ]
  });
}

export function financialOperationalWaterfallOption(data: OperationalWaterfallStep[]): ChartOption {
  void data;
  return {
    "backgroundColor": {
      "type": "radial",
      "x": 0.5,
      "y": 0.42,
      "r": 0.92,
      "colorStops": [
        {
          "offset": 0,
          "color": "rgba(27,42,61,1)"
        },
        {
          "offset": 0.46,
          "color": "rgba(8,12,21,1)"
        },
        {
          "offset": 1,
          "color": "rgba(1,3,8,1)"
        }
      ]
    },
    "animation": true,
    "animationDuration": 1800,
    "animationDurationUpdate": 1100,
    "animationEasing": "elasticOut",
    "animationEasingUpdate": "quarticOut",
    "color": [
      "#d9f7ff",
      "#00f5a0",
      "#ff3864",
      "#7c5cff",
      "#f7c76a",
      "#00b7ff"
    ],
    "title": {
      "show": false,
      "text": "Sovereign Operational Ledger",
      "subtext": "Black-label executive waterfall ledger"
    },
    "aria": {
      "show": true,
      "description": "A high-end dark executive operational waterfall ledger showing gains, losses, totals and net trajectory."
    },
    "textStyle": {
      "color": "#eaf7ff",
      "fontFamily": "Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow",
        "shadowStyle": {
          "color": "rgba(247,199,106,0.07)"
        }
      },
      "backgroundColor": "rgba(3,6,14,0.94)",
      "borderColor": "rgba(247,199,106,0.34)",
      "borderWidth": 1,
      "padding": 12,
      "textStyle": {
        "color": "#f7fbff",
        "fontSize": 12,
        "fontWeight": 800
      },
      "extraCssText": "box-shadow: 0 24px 70px rgba(0,0,0,.62), 0 0 32px rgba(247,199,106,.12); border-radius: 16px; backdrop-filter: blur(18px);"
    },
    "legend": {
      "top": 70,
      "right": 34,
      "itemWidth": 11,
      "itemHeight": 11,
      "itemGap": 18,
      "icon": "roundRect",
      "textStyle": {
        "color": "rgba(224,239,255,0.82)",
        "fontSize": 11,
        "fontWeight": 850
      },
      "data": [
        "Capital lift",
        "Exposure burn",
        "Closing capital",
        "Net trajectory"
      ]
    },
    "grid": {
      "top": 128,
      "left": 72,
      "right": 46,
      "bottom": 104
    },
    "xAxis": {
      "type": "category",
      "data": [
        "OPEN\nCAPITAL",
        "GROWTH\nENGINE",
        "EFFICIENCY\nALPHA",
        "SERVICE\nLOSS",
        "COST\nDRAG",
        "RISK\nADJUST",
        "CLOSE\nCAPITAL"
      ],
      "axisTick": {
        "show": false
      },
      "axisLine": {
        "lineStyle": {
          "color": "rgba(217,247,255,0.22)"
        }
      },
      "axisLabel": {
        "color": "rgba(229,244,255,0.78)",
        "fontSize": 10,
        "fontWeight": 900,
        "lineHeight": 13,
        "margin": 17
      },
      "splitLine": {
        "show": false
      }
    },
    "yAxis": {
      "type": "value",
      "name": "Capital impact / EUR-k",
      "min": 0,
      "max": 1800,
      "interval": 300,
      "nameGap": 20,
      "nameTextStyle": {
        "color": "rgba(247,199,106,0.82)",
        "fontSize": 10,
        "fontWeight": 900
      },
      "axisLabel": {
        "color": "rgba(205,222,240,0.62)",
        "fontSize": 10,
        "fontWeight": 800,
        "formatter": "{value}K"
      },
      "axisLine": {
        "show": false
      },
      "axisTick": {
        "show": false
      },
      "splitLine": {
        "lineStyle": {
          "color": "rgba(217,247,255,0.08)",
          "type": "dashed"
        }
      }
    },
    "graphic": [
      {
        "type": "group",
        "left": 18,
        "top": 16,
        "z": 60,
        "children": [
          {
            "type": "rect",
            "shape": {
              "width": 360,
              "height": 70,
              "r": 20
            },
            "style": {
              "fill": "rgba(4,8,18,0.62)",
              "stroke": "rgba(247,199,106,0.28)",
              "lineWidth": 1,
              "shadowBlur": 34,
              "shadowColor": "rgba(247,199,106,0.12)"
            }
          },
          {
            "type": "rect",
            "left": 14,
            "top": 16,
            "shape": {
              "width": 4,
              "height": 38,
              "r": 2
            },
            "style": {
              "fill": "#f7c76a",
              "shadowBlur": 18,
              "shadowColor": "rgba(247,199,106,0.62)"
            }
          },
          {
            "type": "text",
            "left": 30,
            "top": 13,
            "style": {
              "text": "SOVEREIGN LEDGER",
              "fill": "#fff3c4",
              "fontSize": 14,
              "fontWeight": 950,
              "letterSpacing": 1.8,
              "shadowBlur": 14,
              "shadowColor": "rgba(247,199,106,0.24)"
            }
          },
          {
            "type": "text",
            "left": 30,
            "top": 38,
            "style": {
              "text": "Boardroom-grade operational capital movement",
              "fill": "rgba(219,236,255,0.70)",
              "fontSize": 10,
              "fontWeight": 760
            }
          }
        ]
      },
      {
        "type": "group",
        "right": 24,
        "top": 18,
        "z": 60,
        "children": [
          {
            "type": "rect",
            "shape": {
              "width": 190,
              "height": 62,
              "r": 20
            },
            "style": {
              "fill": "rgba(3,6,14,0.68)",
              "stroke": "rgba(0,245,160,0.26)",
              "lineWidth": 1,
              "shadowBlur": 28,
              "shadowColor": "rgba(0,245,160,0.12)"
            }
          },
          {
            "type": "text",
            "left": 16,
            "top": 10,
            "style": {
              "text": "NET POSITION",
              "fill": "rgba(219,236,255,0.68)",
              "fontSize": 10,
              "fontWeight": 950,
              "letterSpacing": 1.2
            }
          },
          {
            "type": "text",
            "left": 16,
            "top": 27,
            "style": {
              "text": "€650K",
              "fill": "#00f5a0",
              "fontSize": 22,
              "fontWeight": 950,
              "shadowBlur": 16,
              "shadowColor": "rgba(0,245,160,0.42)"
            }
          },
          {
            "type": "text",
            "left": 98,
            "top": 33,
            "style": {
              "text": "CLOSE",
              "fill": "rgba(247,199,106,0.70)",
              "fontSize": 10,
              "fontWeight": 900
            }
          }
        ]
      },
      {
        "type": "group",
        "left": "center",
        "bottom": 18,
        "z": 60,
        "children": [
          {
            "type": "rect",
            "shape": {
              "x": -298,
              "width": 596,
              "height": 54,
              "r": 20
            },
            "style": {
              "fill": "rgba(4,8,18,0.66)",
              "stroke": "rgba(217,247,255,0.12)",
              "lineWidth": 1,
              "shadowBlur": 28,
              "shadowColor": "rgba(0,0,0,0.44)"
            }
          },
          {
            "type": "text",
            "left": -260,
            "top": 9,
            "style": {
              "text": "€780K",
              "fill": "#d9f7ff",
              "fontSize": 16,
              "fontWeight": 950
            }
          },
          {
            "type": "text",
            "left": -260,
            "top": 32,
            "style": {
              "text": "Opening",
              "fill": "rgba(205,222,240,0.62)",
              "fontSize": 9,
              "fontWeight": 800
            }
          },
          {
            "type": "text",
            "left": -108,
            "top": 9,
            "style": {
              "text": "+€780K",
              "fill": "#00f5a0",
              "fontSize": 16,
              "fontWeight": 950
            }
          },
          {
            "type": "text",
            "left": -108,
            "top": 32,
            "style": {
              "text": "Value created",
              "fill": "rgba(205,222,240,0.62)",
              "fontSize": 9,
              "fontWeight": 800
            }
          },
          {
            "type": "text",
            "left": 62,
            "top": 9,
            "style": {
              "text": "-€910K",
              "fill": "#ff3864",
              "fontSize": 16,
              "fontWeight": 950
            }
          },
          {
            "type": "text",
            "left": 62,
            "top": 32,
            "style": {
              "text": "Exposure burn",
              "fill": "rgba(205,222,240,0.62)",
              "fontSize": 9,
              "fontWeight": 800
            }
          },
          {
            "type": "text",
            "left": 224,
            "top": 9,
            "style": {
              "text": "83%",
              "fill": "#f7c76a",
              "fontSize": 16,
              "fontWeight": 950
            }
          },
          {
            "type": "text",
            "left": 224,
            "top": 32,
            "style": {
              "text": "Confidence",
              "fill": "rgba(205,222,240,0.62)",
              "fontSize": 9,
              "fontWeight": 800
            }
          }
        ]
      }
    ],
    "series": [
      {
        "name": "Support",
        "type": "bar",
        "stack": "capital",
        "silent": true,
        "barWidth": 32,
        "data": [
          0,
          780,
          1280,
          1040,
          810,
          650,
          0
        ],
        "itemStyle": {
          "color": "rgba(0,0,0,0)",
          "borderColor": "rgba(0,0,0,0)"
        },
        "emphasis": {
          "disabled": true
        },
        "z": 1
      },
      {
        "name": "Capital lift",
        "type": "bar",
        "stack": "capital",
        "barWidth": 32,
        "data": [
          0,
          {
            "value": 500,
            "label": {
              "formatter": "+500"
            }
          },
          {
            "value": 280,
            "label": {
              "formatter": "+280"
            }
          },
          0,
          0,
          0,
          0
        ],
        "itemStyle": {
          "color": {
            "type": "linear",
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 1,
            "colorStops": [
              {
                "offset": 0,
                "color": "#b6ffe7"
              },
              {
                "offset": 0.38,
                "color": "#00f5a0"
              },
              {
                "offset": 1,
                "color": "#006b4e"
              }
            ]
          },
          "borderColor": "rgba(230,255,246,0.76)",
          "borderWidth": 1,
          "borderRadius": [
            18,
            18,
            18,
            18
          ],
          "shadowBlur": 24,
          "shadowColor": "rgba(0,245,160,0.34)"
        },
        "label": {
          "show": true,
          "position": "top",
          "distance": 10,
          "color": "#b6ffe7",
          "fontSize": 10,
          "fontWeight": 950,
          "backgroundColor": "rgba(0,20,15,0.62)",
          "borderColor": "rgba(0,245,160,0.22)",
          "borderWidth": 1,
          "borderRadius": 8,
          "padding": [
            3,
            7
          ]
        },
        "emphasis": {
          "focus": "series",
          "itemStyle": {
            "shadowBlur": 40,
            "shadowColor": "rgba(0,245,160,0.62)"
          }
        },
        "z": 6
      },
      {
        "name": "Exposure burn",
        "type": "bar",
        "stack": "capital",
        "barWidth": 32,
        "data": [
          0,
          0,
          0,
          {
            "value": 520,
            "label": {
              "formatter": "-520"
            }
          },
          {
            "value": 230,
            "label": {
              "formatter": "-230"
            }
          },
          {
            "value": 160,
            "label": {
              "formatter": "-160"
            }
          },
          0
        ],
        "itemStyle": {
          "color": {
            "type": "linear",
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 1,
            "colorStops": [
              {
                "offset": 0,
                "color": "#ffc1cb"
              },
              {
                "offset": 0.4,
                "color": "#ff3864"
              },
              {
                "offset": 1,
                "color": "#70001d"
              }
            ]
          },
          "borderColor": "rgba(255,232,236,0.72)",
          "borderWidth": 1,
          "borderRadius": [
            18,
            18,
            18,
            18
          ],
          "shadowBlur": 24,
          "shadowColor": "rgba(255,56,100,0.32)"
        },
        "label": {
          "show": true,
          "position": "bottom",
          "distance": 10,
          "color": "#ffc1cb",
          "fontSize": 10,
          "fontWeight": 950,
          "backgroundColor": "rgba(30,0,10,0.62)",
          "borderColor": "rgba(255,56,100,0.22)",
          "borderWidth": 1,
          "borderRadius": 8,
          "padding": [
            3,
            7
          ]
        },
        "emphasis": {
          "focus": "series",
          "itemStyle": {
            "shadowBlur": 40,
            "shadowColor": "rgba(255,56,100,0.58)"
          }
        },
        "z": 6
      },
      {
        "name": "Closing capital",
        "type": "bar",
        "barWidth": 42,
        "data": [
          {
            "value": 780,
            "label": {
              "formatter": "780"
            }
          },
          0,
          0,
          0,
          0,
          0,
          {
            "value": 650,
            "label": {
              "formatter": "650"
            }
          }
        ],
        "itemStyle": {
          "color": {
            "type": "linear",
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 1,
            "colorStops": [
              {
                "offset": 0,
                "color": "#ffffff"
              },
              {
                "offset": 0.36,
                "color": "#d9f7ff"
              },
              {
                "offset": 1,
                "color": "#173a70"
              }
            ]
          },
          "borderColor": "rgba(255,255,255,0.92)",
          "borderWidth": 1.2,
          "borderRadius": [
            20,
            20,
            20,
            20
          ],
          "shadowBlur": 34,
          "shadowColor": "rgba(217,247,255,0.34)"
        },
        "label": {
          "show": true,
          "position": "top",
          "distance": 10,
          "color": "#ffffff",
          "fontSize": 11,
          "fontWeight": 950,
          "backgroundColor": "rgba(7,14,31,0.70)",
          "borderColor": "rgba(217,247,255,0.26)",
          "borderWidth": 1,
          "borderRadius": 8,
          "padding": [
            3,
            8
          ]
        },
        "emphasis": {
          "focus": "series",
          "itemStyle": {
            "shadowBlur": 48,
            "shadowColor": "rgba(217,247,255,0.60)"
          }
        },
        "z": 7
      },
      {
        "name": "Net trajectory",
        "type": "line",
        "smooth": true,
        "symbol": "diamond",
        "symbolSize": 9,
        "data": [
          780,
          1280,
          1560,
          1040,
          810,
          650,
          650
        ],
        "lineStyle": {
          "color": "#f7c76a",
          "width": 3,
          "shadowBlur": 18,
          "shadowColor": "rgba(247,199,106,0.42)"
        },
        "itemStyle": {
          "color": "#080c15",
          "borderColor": "#f7c76a",
          "borderWidth": 2,
          "shadowBlur": 16,
          "shadowColor": "rgba(247,199,106,0.46)"
        },
        "areaStyle": {
          "opacity": 0.13,
          "color": {
            "type": "linear",
            "x": 0,
            "y": 0,
            "x2": 0,
            "y2": 1,
            "colorStops": [
              {
                "offset": 0,
                "color": "rgba(247,199,106,0.32)"
              },
              {
                "offset": 1,
                "color": "rgba(247,199,106,0)"
              }
            ]
          }
        },
        "label": {
          "show": false
        },
        "emphasis": {
          "focus": "series",
          "lineStyle": {
            "width": 4.5,
            "shadowBlur": 30,
            "shadowColor": "rgba(247,199,106,0.72)"
          }
        },
        "z": 10
      }
    ]
  } as ChartOption;
}

export function shiftPulseStripOption(data: ShiftPulseBucket[]): ChartOption {
  const buckets = data.length > 0 ? data : [];
  const labels = buckets.map((bucket) => timeLabel(bucket.bucketStart));
  const ticketCounts = buckets.map((bucket) => bucket.saleCount);
  const sales = buckets.map((bucket) => bucket.grossSales);
  const offlineCounts = buckets.map((bucket) => bucket.offlineSaleCount);
  const queuePressure = buckets.map((bucket) => bucket.queuePressure);
  const peakSales = sales.reduce((max, value) => Math.max(max, value), 0);
  const peakQueue = queuePressure.reduce((max, value) => Math.max(max, value), 0);
  const totalOffline = offlineCounts.reduce((sum, value) => sum + value, 0);
  const salesMin = Math.max(0, Math.min(...sales, 0));
  const salesMax = Math.max(1000, Math.ceil((peakSales * 1.12) / 1000) * 1000);
  const peakSalesLabel = formatCurrencyFromCents(peakSales);
  const rushIndex = sales.findIndex((value) => value === peakSales);
  const rushLabel = rushIndex >= 0 ? labels[rushIndex] : "--";

  return mergeBase("Shift Pulse Strip", "Compact shift pulse for sales, ticket count, offline sales, and queue pressure.", {
    backgroundColor: {
      type: "radial",
      x: 0.5,
      y: 0.38,
      r: 0.95,
      colorStops: [
        { offset: 0, color: "rgba(22, 45, 76, 0.98)" },
        { offset: 0.46, color: "rgba(8, 14, 28, 0.98)" },
        { offset: 1, color: "rgba(1, 4, 10, 1)" }
      ]
    },
    animationDuration: 1200,
    animationDurationUpdate: 850,
    animationEasing: "cubicOut",
    animationEasingUpdate: "quarticOut",
    aria: {
      show: true,
      description: "Premium compact shift pulse showing tickets, sales, offline transactions, and queue pressure for a clean mock/demo or adapter-backed scenario."
    },
    textStyle: {
      color: "#eaf6ff",
      fontFamily: "Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif"
    },
    tooltip: {
      trigger: "axis",
      confine: true,
      backgroundColor: "rgba(3, 7, 16, 0.94)",
      borderColor: "rgba(111, 224, 255, 0.28)",
      borderWidth: 1,
      padding: 12,
      extraCssText: "box-shadow: 0 24px 70px rgba(0,0,0,.56), 0 0 28px rgba(99,223,255,.10); border-radius: 16px; backdrop-filter: blur(16px);",
      textStyle: { color: "#f4fbff", fontSize: 12, fontWeight: 800 },
      axisPointer: {
        type: "shadow",
        shadowStyle: { color: "rgba(99, 223, 255, 0.08)" },
        label: { show: true, backgroundColor: "rgba(6, 14, 30, 0.92)", color: "#eaf6ff", fontWeight: 900 }
      },
      formatter: (params: unknown) => {
        const item = itemByTooltipIndex(buckets, params);
        return item
          ? `${tooltipLabel(params)}<br/>Tickets: ${item.saleCount}<br/>Ventas: ${formatCurrencyFromCents(item.grossSales)}<br/>Offline: ${item.offlineSaleCount}<br/>Pendiente sync: ${item.pendingSyncCount}<br/>Presión: ${item.queuePressure}/100<br/>Estado: ${item.status}`
          : tooltipLabel(params);
      }
    },
    legend: {
      top: 68,
      right: 28,
      itemWidth: 12,
      itemHeight: 12,
      itemGap: 18,
      icon: "roundRect",
      textStyle: { color: "rgba(226, 241, 255, 0.82)", fontSize: 11, fontWeight: 850 },
      data: ["Tickets", "Ventas", "Offline", "Queue pressure"]
    },
    grid: { top: 112, left: 54, right: 42, bottom: 46, containLabel: false },
    xAxis: {
      type: "category",
      boundaryGap: true,
      data: labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: "rgba(216, 225, 236, 0.22)" } },
      axisLabel: { color: "rgba(216, 225, 236, 0.72)", fontSize: 10, fontWeight: 850, margin: 15 },
      splitLine: { show: false }
    },
    yAxis: [
      {
        type: "value",
        name: "Tickets / pressure",
        min: 0,
        max: Math.max(24, Math.ceil((Math.max(...ticketCounts, peakQueue, 1) * 1.18) / 6) * 6),
        interval: 6,
        nameGap: 20,
        nameTextStyle: { color: "rgba(99, 223, 255, 0.62)", fontSize: 10, fontWeight: 900 },
        axisLabel: { color: "rgba(216, 225, 236, 0.58)", fontSize: 10, fontWeight: 800 },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "rgba(216, 225, 236, 0.075)", type: "dashed" } }
      },
      { type: "value", show: false, min: salesMin, max: salesMax }
    ],
    graphic: [
      {
        type: "group",
        left: 18,
        top: 14,
        z: 70,
        children: [
          { type: "rect", shape: { width: 352, height: 66, r: 20 }, style: { fill: "rgba(4, 9, 20, 0.66)", stroke: "rgba(99, 223, 255, 0.22)", lineWidth: 1, shadowBlur: 34, shadowColor: "rgba(99, 223, 255, 0.12)" } },
          { type: "rect", left: 14, top: 15, shape: { width: 4, height: 36, r: 2 }, style: { fill: "#63dfff", shadowBlur: 18, shadowColor: "rgba(99, 223, 255, 0.58)" } },
          { type: "text", left: 30, top: 12, style: { text: "SHIFT PULSE STRIP", fill: "#ecfbff", fontSize: 14, fontWeight: 950, shadowBlur: 14, shadowColor: "rgba(99, 223, 255, 0.28)" } },
          { type: "text", left: 30, top: 37, style: { text: "Sales heat · queue pressure · offline watch · mock/demo or adapter", fill: "rgba(216, 225, 236, 0.68)", fontSize: 10, fontWeight: 760 } }
        ]
      },
      {
        type: "group",
        right: 24,
        top: 14,
        z: 70,
        children: [
          { type: "rect", shape: { width: 348, height: 66, r: 20 }, style: { fill: "rgba(4, 9, 20, 0.64)", stroke: "rgba(229, 155, 42, 0.30)", lineWidth: 1, shadowBlur: 32, shadowColor: "rgba(229, 155, 42, 0.12)" } },
          { type: "text", left: 18, top: 10, style: { text: "PEAK SALES", fill: "rgba(216, 225, 236, 0.66)", fontSize: 9, fontWeight: 950 } },
          { type: "text", left: 18, top: 28, style: { text: peakSalesLabel, fill: "#ffc86d", fontSize: 22, fontWeight: 950, shadowBlur: 16, shadowColor: "rgba(229, 155, 42, 0.45)" } },
          { type: "text", left: 120, top: 10, style: { text: "QUEUE", fill: "rgba(216, 225, 236, 0.66)", fontSize: 9, fontWeight: 950 } },
          { type: "text", left: 120, top: 31, style: { text: `${peakQueue}/100`, fill: peakQueue >= 70 ? "#ff5c7a" : "#63dfff", fontSize: 18, fontWeight: 950, shadowBlur: 12, shadowColor: "rgba(255, 92, 122, 0.34)" } },
          { type: "text", left: 214, top: 10, style: { text: "OFFLINE", fill: "rgba(216, 225, 236, 0.66)", fontSize: 9, fontWeight: 950 } },
          { type: "text", left: 214, top: 31, style: { text: String(totalOffline), fill: "#7c5cff", fontSize: 18, fontWeight: 950, shadowBlur: 12, shadowColor: "rgba(124, 92, 255, 0.38)" } },
          { type: "text", left: 278, top: 33, style: { text: rushLabel, fill: "rgba(99, 223, 255, 0.74)", fontSize: 10, fontWeight: 900 } }
        ]
      }
    ],
    series: [
      {
        type: "bar",
        name: "Tickets",
        barWidth: 26,
        data: buckets.map((bucket) => ({
          value: bucket.saleCount,
          shiftBucket: bucket,
          itemStyle: bucket.status === "blocked" || bucket.status === "risk" ? { shadowBlur: 32, shadowColor: "rgba(255, 92, 122, 0.45)" } : undefined,
          label: bucket.saleCount === Math.max(...ticketCounts, 0) ? { show: true, formatter: String(bucket.saleCount) } : undefined
        })),
        itemStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#e5fbff" }, { offset: 0.42, color: "#63dfff" }, { offset: 1, color: "#086dff" }] },
          borderColor: "rgba(229, 251, 255, 0.62)",
          borderWidth: 1,
          borderRadius: [12, 12, 4, 4],
          shadowBlur: 18,
          shadowColor: "rgba(99, 223, 255, 0.24)"
        },
        label: { show: true, position: "top", distance: 8, color: "#eaf6ff", fontSize: 10, fontWeight: 950, backgroundColor: "rgba(3, 7, 16, 0.56)", borderColor: "rgba(99, 223, 255, 0.18)", borderWidth: 1, borderRadius: 8, padding: [2, 6] },
        emphasis: { focus: "series", itemStyle: { shadowBlur: 42, shadowColor: "rgba(99, 223, 255, 0.68)" } },
        z: 5
      },
      {
        type: "bar",
        name: "Offline",
        barWidth: 10,
        barGap: "-62%",
        data: buckets.map((bucket) => ({ value: bucket.offlineSaleCount, shiftBucket: bucket })),
        itemStyle: {
          color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#d9ceff" }, { offset: 0.46, color: "#7c5cff" }, { offset: 1, color: "#25125f" }] },
          borderRadius: [8, 8, 3, 3],
          shadowBlur: 18,
          shadowColor: "rgba(124, 92, 255, 0.34)"
        },
        label: { show: false, position: "top", distance: 6, color: "#d9ceff", fontSize: 10, fontWeight: 950 },
        emphasis: { focus: "series" },
        z: 7
      },
      {
        type: "line",
        name: "Queue pressure",
        data: buckets.map((bucket) => ({
          value: bucket.queuePressure,
          shiftBucket: bucket,
          symbolSize: bucket.queuePressure >= 70 ? 12 : 7,
          label: bucket.queuePressure === peakQueue ? { show: true, formatter: `${bucket.queuePressure}/100` } : undefined
        })),
        smooth: true,
        symbol: "circle",
        symbolSize: 7,
        lineStyle: { color: "#ff5c7a", width: 2.6, shadowBlur: 16, shadowColor: "rgba(255, 92, 122, 0.42)" },
        itemStyle: { color: "#050914", borderColor: "#ff5c7a", borderWidth: 2, shadowBlur: 14, shadowColor: "rgba(255, 92, 122, 0.38)" },
        areaStyle: { opacity: 0.12, color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(255, 92, 122, 0.34)" }, { offset: 1, color: "rgba(255, 92, 122, 0)" }] } },
        label: { show: false, position: "top", distance: 10, color: "#ffd8df", fontSize: 10, fontWeight: 950, backgroundColor: "rgba(28, 3, 13, 0.68)", borderColor: "rgba(255, 92, 122, 0.24)", borderWidth: 1, borderRadius: 8, padding: [2, 6] },
        emphasis: { focus: "series", lineStyle: { width: 3.4, shadowBlur: 28, shadowColor: "rgba(255, 92, 122, 0.66)" } },
        z: 8
      },
      {
        type: "line",
        name: "Ventas",
        yAxisIndex: 1,
        data: buckets.map((bucket) => ({
          value: bucket.grossSales,
          shiftBucket: bucket,
          symbolSize: bucket.grossSales === peakSales ? 13 : bucket.queuePressure >= 55 ? 10 : 7,
          label: bucket.grossSales === peakSales ? { show: true, formatter: formatCurrencyFromCents(bucket.grossSales) } : undefined
        })),
        smooth: true,
        symbol: "diamond",
        symbolSize: 8,
        lineStyle: { color: "#ffc86d", width: 3.4, shadowBlur: 20, shadowColor: "rgba(229, 155, 42, 0.48)" },
        itemStyle: { color: "#050914", borderColor: "#ffc86d", borderWidth: 2, shadowBlur: 16, shadowColor: "rgba(229, 155, 42, 0.44)" },
        areaStyle: { opacity: 0.16, color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(255, 200, 109, 0.36)" }, { offset: 1, color: "rgba(255, 200, 109, 0)" }] } },
        label: { show: false, position: "top", distance: 12, color: "#fff1c7", fontSize: 10, fontWeight: 950, backgroundColor: "rgba(28, 17, 3, 0.70)", borderColor: "rgba(229, 155, 42, 0.26)", borderWidth: 1, borderRadius: 8, padding: [3, 7] },
        markArea: rushIndex >= 0 ? { silent: true, itemStyle: { color: "rgba(255, 200, 109, 0.055)" }, data: [[{ name: "rush window", xAxis: labels[rushIndex] }, { xAxis: labels[Math.min(labels.length - 1, rushIndex + 1)] ?? labels[rushIndex] }]] } : undefined,
        emphasis: { focus: "series", lineStyle: { width: 4.4, shadowBlur: 32, shadowColor: "rgba(229, 155, 42, 0.72)" } },
        z: 10
      }
    ],
    color: ["#086dff", "#63dfff", "#13b981", "#e59b2a", "#df3d2f", "#7557ff"]
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
    tooltip: {
      formatter: (params: unknown) => {
        const item = asRecord(tooltipDataArray(params)[3]) as Partial<SyncOutboxMatrixCell> | null;
        return item
          ? `${humanizeKey(String(item.itemType ?? ""))} / ${item.syncState ?? ""}<br/>Count: ${safeNumber(item.count)}<br/>Oldest: ${formatAgeMinutes(safeNumber(item.oldestAgeMinutes))}<br/>Retries: ${safeNumber(item.retryCount)}<br/>Blocking: ${item.blocking ? "yes" : "no"}`
          : tooltipLabel(params);
      }
    },
    series: [{ type: "heatmap", data: values, label: { show: true, color: "#fff", fontWeight: 900 }, emphasis: { itemStyle: { borderColor: "#fff", borderWidth: 1 } } }]
  });
}

export function ownerPulseTimelineOption(data: OwnerPulsePoint[]): ChartOption {
  return mergeBase("Owner Pulse Timeline", "Mobile owner pulse showing recent health trend, incidents, and actions.", {
    grid: { top: 12, left: 38, right: 12, bottom: 32 },
    xAxis: { type: "category", data: data.map((point) => timeLabel(point.time)), axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#d8e1ec" } },
    tooltip: {
      formatter: (params: unknown) => {
        const item = itemByTooltipIndex(data, params);
        const value = firstTooltipParam(params)?.value;
        return item
          ? `${tooltipLabel(params)}<br/>Health: ${safeNumber(value, item.healthScore)}<br/>Incidents: ${item.activeIncidentCount}<br/>Actions: ${item.openActionCount}<br/>Confidence: ${formatPercent(item.dataConfidence)}`
          : tooltipLabel(params);
      }
    },
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
    tooltip: {
      formatter: (params: unknown) => {
        const item = itemByTooltipIndex(data, params);
        return item
          ? `${item.moduleName}<br/>${item.freshnessState}<br/>Age: ${formatAgeMinutes(item.staleMinutes)}<br/>Source: ${item.source}<br/>Confidence: ${formatPercent(item.confidence)}`
          : tooltipLabel(params);
      }
    },
    series: [{ type: "pictorialBar", symbol: "roundRect", symbolRepeat: true, symbolSize: [22, 10], symbolMargin: 2, data: data.map((item) => ({ value: freshnessScore(item), itemStyle: { color: statusColor(item.freshnessState) } })) }]
  });
}

export function incidentSparkOption(card: IncidentSparkCard): ChartOption {
  return mergeBase(card.title, `Sparkline for incident ${card.incidentId}.`, {
    grid: { top: 8, left: 8, right: 8, bottom: 8 },
    xAxis: { type: "category", show: false, data: card.points.map((point) => timeLabel(point.time)) },
    yAxis: { type: "value", show: false, min: 0, max: 100 },
    tooltip: { formatter: (params: unknown) => `${card.title}<br/>Impact: ${safeNumber(firstTooltipParam(params)?.value)}<br/>Action: ${card.recommendedNextAction}` },
    series: [{ type: "line", data: card.points.map((point) => point.impactScore), smooth: true, symbol: "none", lineStyle: { color: severityColor(card.severity), width: 3 }, areaStyle: { color: "rgba(99,223,255,.10)" } }]
  });
}

export function confidenceMeterBandsOption(data: ConfidenceBand[]): ChartOption {
  return mergeBase("Confidence Meter Bands", "Linear confidence bands explaining why the mobile snapshot can or cannot be trusted.", {
    grid: { top: 12, left: 94, right: 18, bottom: 28 },
    xAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#d8e1ec" } },
    yAxis: { type: "category", data: data.map((item) => item.label), axisLabel: { color: "#f8fafc", fontWeight: 800 } },
    tooltip: {
      formatter: (params: unknown) => {
        const item = itemByTooltipIndex(data, params);
        const value = firstTooltipParam(params)?.value;
        return item
          ? `${item.label}<br/>${safeNumber(value, item.value)}<br/>${item.reason}<br/>Modules: ${item.affectedModules.join(", ")}`
          : tooltipLabel(params);
      }
    },
    series: [{ type: "bar", data: data.map((item) => ({ value: item.value, itemStyle: { color: statusColor(item.state), borderRadius: [0, 999, 999, 0] } })), label: { show: true, position: "right", formatter: (params: unknown) => formatPercent(safeNumber(firstTooltipParam(params)?.value)), color: "#f8fafc", fontWeight: 900 } }]
  });
}
