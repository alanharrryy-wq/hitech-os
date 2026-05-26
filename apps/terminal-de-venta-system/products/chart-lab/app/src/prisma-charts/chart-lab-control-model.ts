// PRISMA_CHART_LAB_POWER_STUDIO_V3_FINAL_INFRASTRUCTURE
// PRISMA_PEARL_EXECUTIVE_CONTROL_PRESETS_V1
import type {
  LabChartControlState,
  LabChartControlValue,
  LabChartRuntimeControl,
  LabChartScenario,
  LabChartThemePreset
} from "./chart-lab-types";

const severityOptions = ["INFO", "WARN", "ERROR", "CRITICAL"].map((value) => ({ label: value, value }));
const scenarioOptions = [
  { label: "Clean", value: "clean" },
  { label: "Critical", value: "critical" },
  { label: "Partial", value: "partial" },
  { label: "Stale", value: "stale" },
  { label: "Offline", value: "offline" },
  { label: "Dense", value: "dense-noir" }
];
const themeOptions = [
  { label: "Crystal", value: "crystal-light" },
  { label: "Executive Dense", value: "executive-dense" },
  { label: "Forensic", value: "forensic" },
  { label: "High Contrast", value: "high-contrast" }
];

function control(input: LabChartRuntimeControl): LabChartRuntimeControl {
  return input;
}

function commonChartControls(extra: LabChartRuntimeControl[] = []): LabChartRuntimeControl[] {
  return [
    control({
      id: "dataScenario",
      label: "Data scenario",
      type: "select",
      defaultValue: "clean",
      options: scenarioOptions,
      affectedLayer: "data",
      affectedDataTransform: "scales or suppresses mock values to preview state behavior",
      validation: "value must be one of clean, critical, partial, stale, offline, dense",
      risk: "low",
      resetBehavior: "returns to clean",
      powerTab: "data"
    }),
    control({
      id: "themePreset",
      label: "Theme preset",
      type: "segmented",
      defaultValue: "crystal-light",
      options: themeOptions,
      affectedLayer: "visual recipe",
      affectedOptionPath: "option.color / option.backgroundColor / textStyle",
      validation: "value must be a known lab theme preset",
      risk: "low",
      resetBehavior: "returns to Crystal Light",
      powerTab: "visual"
    }),
    control({
      id: "showLabels",
      label: "Labels",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "chart marks",
      affectedOptionPath: "series[].label.show",
      validation: "boolean",
      risk: "low",
      resetBehavior: "labels on",
      powerTab: "labels"
    }),
    control({
      id: "animation",
      label: "Animation",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "motion",
      affectedOptionPath: "option.animation",
      validation: "boolean; disabled when reduced motion is active",
      risk: "low",
      resetBehavior: "animation on",
      powerTab: "motion"
    }),
    control({
      id: "visualIntensity",
      label: "Visual intensity",
      type: "range",
      defaultValue: 70,
      min: 20,
      max: 200,
      step: 5,
      affectedLayer: "marks",
      affectedOptionPath: "series[].itemStyle.opacity / lineStyle.width / itemStyle.shadowBlur",
      validation: "20-200; safe up to 100, wild 101-160, insane 161-200",
      risk: "medium",
      resetBehavior: "returns to 70",
      powerTab: "visual"
    }),
    control({
      id: "contrastPunch",
      label: "Contrast punch",
      type: "range",
      defaultValue: 72,
      min: 0,
      max: 200,
      step: 4,
      affectedLayer: "visual emphasis",
      affectedOptionPath: "series[].itemStyle.borderWidth / lineStyle.opacity / emphasis",
      validation: "0-200; boosts visual separation without changing data",
      risk: "medium",
      resetBehavior: "returns to 72",
      powerTab: "visual"
    }),
    control({
      id: "glowAura",
      label: "Glow aura",
      type: "range",
      defaultValue: 8,
      min: 0,
      max: 80,
      step: 2,
      affectedLayer: "visual atmosphere",
      affectedOptionPath: "series[].itemStyle.shadowBlur / lineStyle.shadowBlur",
      validation: "0-80; safe up to 24, wild 25-55, insane 56-80",
      risk: "medium",
      resetBehavior: "returns to 8",
      powerTab: "visual"
    }),
    control({
      id: "motionPreset",
      label: "Motion preset",
      type: "segmented",
      defaultValue: "subtle-premium",
      options: [
        { label: "Still", value: "still" },
        { label: "Subtle", value: "subtle-premium" },
        { label: "Sweep", value: "sweep-scan" },
        { label: "Pulse", value: "pulse-alerts" },
        { label: "Snap", value: "executive-snap" }
      ],
      affectedLayer: "motion recipe",
      affectedOptionPath: "option.animation*",
      validation: "known motion recipe",
      risk: "low",
      resetBehavior: "returns to Subtle",
      powerTab: "motion"
    }),
    control({
      id: "entranceDuration",
      label: "Entrance duration",
      type: "range",
      defaultValue: 900,
      min: 0,
      max: 5000,
      step: 100,
      affectedLayer: "motion",
      affectedOptionPath: "option.animationDuration",
      validation: "0-5000 ms",
      risk: "medium",
      resetBehavior: "900 ms",
      powerTab: "motion"
    }),
    control({
      id: "updateDuration",
      label: "Update duration",
      type: "range",
      defaultValue: 900,
      min: 0,
      max: 5000,
      step: 100,
      affectedLayer: "motion",
      affectedOptionPath: "option.animationDurationUpdate",
      validation: "0-5000 ms",
      risk: "medium",
      resetBehavior: "900 ms",
      powerTab: "motion"
    }),
    control({
      id: "staggerDelay",
      label: "Stagger delay",
      type: "range",
      defaultValue: 20,
      min: 0,
      max: 1500,
      step: 20,
      affectedLayer: "motion",
      affectedOptionPath: "option.animationDelay / option.animationDelayUpdate",
      validation: "0-1500 ms",
      risk: "medium",
      resetBehavior: "20 ms",
      powerTab: "motion"
    }),
    control({
      id: "easingCurve",
      label: "Easing",
      type: "select",
      defaultValue: "cubicOut",
      options: [
        { label: "Linear", value: "linear" },
        { label: "Cubic out", value: "cubicOut" },
        { label: "Quartic out", value: "quarticOut" },
        { label: "Elastic out", value: "elasticOut" },
        { label: "Bounce out", value: "bounceOut" }
      ],
      affectedLayer: "motion",
      affectedOptionPath: "option.animationEasing / option.animationEasingUpdate",
      validation: "known ECharts easing string",
      risk: "low",
      resetBehavior: "cubicOut",
      powerTab: "motion"
    }),
    control({
      id: "tooltipMode",
      label: "Tooltip mode",
      type: "segmented",
      defaultValue: "rich",
      options: [
        { label: "None", value: "none" },
        { label: "Simple", value: "simple" },
        { label: "Rich", value: "rich" },
        { label: "Forensic", value: "forensic" }
      ],
      affectedLayer: "interaction",
      affectedOptionPath: "option.tooltip",
      validation: "tooltip presentation only",
      risk: "low",
      resetBehavior: "rich",
      powerTab: "interaction"
    }),
    control({
      id: "hoverSpotlight",
      label: "Hover spotlight",
      type: "segmented",
      defaultValue: "soft",
      options: [
        { label: "Off", value: "off" },
        { label: "Soft", value: "soft" },
        { label: "Strong", value: "strong" }
      ],
      affectedLayer: "interaction",
      affectedOptionPath: "series[].emphasis / series[].blur",
      validation: "focuses hovered marks while dimming surrounding noise",
      risk: "medium",
      resetBehavior: "soft",
      powerTab: "interaction"
    }),
    ...extra
  ];
}

export const chartControlSchemas: Record<string, LabChartRuntimeControl[]> = {
  "pc.causal-flow-ribbon": commonChartControls([
    control({
      id: "severityFilter",
      label: "Severity",
      type: "chip-group",
      defaultValue: ["INFO", "WARN", "ERROR", "CRITICAL"],
      options: severityOptions,
      affectedLayer: "data links",
      affectedDataTransform: "filters sankey links by datum.severity",
      validation: "one or more known severity values",
      risk: "medium",
      resetBehavior: "all severities enabled"
    }),
    control({
      id: "confidenceFloor",
      label: "Confidence floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "data links",
      affectedDataTransform: "filters links below confidence threshold",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "ribbonWidth",
      label: "Ribbon width",
      type: "range",
      defaultValue: 14,
      min: 8,
      max: 120,
      step: 1,
      affectedLayer: "geometry",
      affectedOptionPath: "series[0].nodeWidth",
      validation: "8-120; safe 8-26, wild 27-60, insane 61-120",
      risk: "medium",
      resetBehavior: "14",
      powerTab: "visual"
    }),
    control({
      id: "ribbonOpacity",
      label: "Ribbon opacity",
      type: "range",
      defaultValue: 46,
      min: 0,
      max: 100,
      step: 2,
      affectedLayer: "links",
      affectedOptionPath: "series[0].links[].lineStyle.opacity",
      validation: "0-100; safe 25-90, wild 10-24 or 91-100, insane 0-9",
      risk: "medium",
      resetBehavior: "46",
      powerTab: "visual"
    }),
    control({
      id: "detailLevel",
      label: "Detail level",
      type: "segmented",
      defaultValue: "standard",
      options: [
        { label: "Calm", value: "calm-night" },
        { label: "Standard", value: "standard" },
        { label: "Forensic", value: "forensic" }
      ],
      affectedLayer: "labels/tooltips",
      affectedOptionPath: "series[0].label / tooltip",
      validation: "calm, standard, forensic",
      risk: "low",
      resetBehavior: "standard"
    }),
    control({
      id: "stageFocus",
      label: "Stage focus",
      type: "select",
      defaultValue: "all",
      options: [
        { label: "All stages", value: "all" },
        { label: "Source", value: "sourceModule" },
        { label: "Cause", value: "causeType" },
        { label: "Effect", value: "effectType" },
        { label: "Action", value: "actionTarget" }
      ],
      affectedLayer: "data links",
      affectedDataTransform: "keeps links connected to the selected causal stage",
      validation: "known causal stage",
      risk: "medium",
      resetBehavior: "all"
    }),
    control({
      id: "layoutDensity",
      label: "Layout density",
      type: "segmented",
      defaultValue: "balanced",
      options: [
        { label: "Airy", value: "airy" },
        { label: "Balanced", value: "balanced" },
        { label: "Dense", value: "dense-noir" }
      ],
      affectedLayer: "layout",
      affectedOptionPath: "series[0].nodeGap / layoutIterations",
      validation: "airy, balanced, dense",
      risk: "medium",
      resetBehavior: "balanced"
    }),
    control({
      id: "evidenceMode",
      label: "Evidence mode",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "tooltip/labels",
      affectedOptionPath: "series[0].edgeLabel.show",
      validation: "boolean",
      risk: "low",
      resetBehavior: "enabled"
    })
  ]),
  "pc.operational-density-field": commonChartControls([
    control({
      id: "pressureFloor",
      label: "Pressure floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "heatmap data",
      affectedDataTransform: "filters heatmap cells below pressure",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "moduleSearch",
      label: "Module search",
      type: "search",
      defaultValue: "",
      affectedLayer: "heatmap rows",
      affectedDataTransform: "filters y-axis modules",
      validation: "plain text",
      risk: "low",
      resetBehavior: "empty"
    })
  ]),
  "ops.operational-density-heatmap": commonChartControls([
    control({
      id: "heatPalette",
      label: "Heat palette",
      type: "segmented",
      defaultValue: "control-spectrum",
      options: [
        { label: "Controls", value: "control-spectrum" },
        { label: "Thermal", value: "thermal" },
        { label: "Aurora", value: "aurora" },
        { label: "Critical", value: "critical" }
      ],
      affectedLayer: "visualMap.inRange.color",
      affectedOptionPath: "visualMap[].inRange.color",
      validation: "known heatmap palette",
      risk: "low",
      resetBehavior: "returns to PRISMA control-spectrum palette"
    }),
    control({
      id: "heatZoneMode",
      label: "Heat zones",
      type: "segmented",
      defaultValue: "balanced",
      options: [
        { label: "Balanced", value: "balanced" },
        { label: "Gateway noon", value: "gateway-noon" },
        { label: "Payments night", value: "payments-night" },
        { label: "Ops wave", value: "ops-wave" },
        { label: "Stress demo", value: "stress-demo" }
      ],
      affectedLayer: "series[0].data.value[2]",
      affectedDataTransform: "lab-only deterministic heat-zone transform for preview storytelling",
      validation: "known heat-zone mode",
      risk: "low",
      resetBehavior: "balanced distribution"
    }),
    control({
      id: "heatIntensity",
      label: "Heat intensity",
      type: "range",
      defaultValue: 112,
      min: 70,
      max: 150,
      step: 2,
      affectedLayer: "series[0].data.value[2]",
      affectedDataTransform: "scales pressure values for visual stress testing without source writes",
      validation: "70-150",
      risk: "low",
      resetBehavior: "112"
    }),
    control({
      id: "hotspotBias",
      label: "Hotspot bias",
      type: "range",
      defaultValue: 18,
      min: 0,
      max: 42,
      step: 1,
      affectedLayer: "series[0].data.value[2]",
      affectedDataTransform: "adds localized heat near the selected operational zone",
      validation: "0-42",
      risk: "low",
      resetBehavior: "18"
    }),
    control({
      id: "heatCeiling",
      label: "Heat ceiling",
      type: "range",
      defaultValue: 90,
      min: 72,
      max: 100,
      step: 1,
      affectedLayer: "visualMap.max",
      affectedOptionPath: "visualMap[].max",
      validation: "72-100",
      risk: "low",
      resetBehavior: "90"
    }),
    control({
      id: "gridVisibility",
      label: "Cell grid",
      type: "range",
      defaultValue: 18,
      min: 0,
      max: 55,
      step: 1,
      affectedLayer: "series[0].itemStyle.borderColor",
      affectedOptionPath: "series[0].itemStyle.borderColor",
      validation: "0-55",
      risk: "low",
      resetBehavior: "18"
    }),
    control({
      id: "showCellNumbers",
      label: "Cell numbers",
      type: "toggle",
      defaultValue: false,
      affectedLayer: "series[0].label.show",
      affectedOptionPath: "series[0].label.show",
      validation: "boolean",
      risk: "low",
      resetBehavior: "disabled"
    }),
    control({
      id: "showCallouts",
      label: "Callouts",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "graphic[].invisible",
      affectedOptionPath: "graphic[].invisible",
      validation: "boolean",
      risk: "low",
      resetBehavior: "enabled"
    }),
    control({
      id: "motionMode",
      label: "Motion",
      type: "segmented",
      defaultValue: "sweep",
      options: [
        { label: "Still", value: "still" },
        { label: "Sweep", value: "sweep" },
        { label: "Pulse", value: "pulse" }
      ],
      affectedLayer: "animation + CSS frame aura",
      affectedOptionPath: "animation",
      validation: "still, sweep, pulse",
      risk: "low",
      resetBehavior: "sweep"
    })
  ]),
  "pc.service-dependency-graph": commonChartControls([
    control({
      id: "dependencyStatus",
      label: "Dependency status",
      type: "chip-group",
      defaultValue: ["PASS", "DEGRADED", "FAIL", "UNKNOWN"],
      options: ["PASS", "DEGRADED", "FAIL", "UNKNOWN"].map((value) => ({ label: value, value })),
      affectedLayer: "graph nodes",
      affectedDataTransform: "filters nodes and edges by status",
      validation: "one or more known status values",
      risk: "medium",
      resetBehavior: "all statuses enabled"
    }),
    control({
      id: "forceRepulsion",
      label: "Repulsion",
      type: "range",
      defaultValue: 210,
      min: 90,
      max: 420,
      step: 10,
      affectedLayer: "layout physics",
      affectedOptionPath: "series[0].force.repulsion",
      validation: "90-420",
      risk: "medium",
      resetBehavior: "210"
    })
  ]),
  "pc.inventory-risk-treemap": commonChartControls([
    control({
      id: "riskFloor",
      label: "Risk floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "treemap nodes",
      affectedDataTransform: "filters low-risk nodes",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "leafDepth",
      label: "Leaf depth",
      type: "segmented",
      defaultValue: "category",
      options: [
        { label: "Category", value: "category" },
        { label: "SKU", value: "sku" }
      ],
      affectedLayer: "treemap hierarchy",
      affectedOptionPath: "series[0].leafDepth",
      validation: "category or sku",
      risk: "low",
      resetBehavior: "category"
    })
  ]),
  "pc.decision-ledger-timeline": commonChartControls([
    // PRISMA_DECISION_LEDGER_CONTROL_DECK_V1: deeper controls for audit timeline exploration.
    control({
      id: "impactFloor",
      label: "Impact floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "timeline points",
      affectedDataTransform: "filters decision points below impact",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "confidenceFloor",
      label: "Confidence floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "timeline points",
      affectedDataTransform: "filters decision points below confidence",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "evidenceFloor",
      label: "Evidence floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 10,
      step: 1,
      affectedLayer: "timeline evidence",
      affectedDataTransform: "keeps only points with enough evidence",
      validation: "0-10",
      risk: "medium",
      resetBehavior: "0"
    }),
    control({
      id: "ledgerStatus",
      label: "Status",
      type: "chip-group",
      defaultValue: ["open", "in_progress", "resolved", "blocked"],
      options: ["open", "in_progress", "resolved", "blocked"].map((value) => ({ label: value.replace("_", " "), value })),
      affectedLayer: "timeline events",
      affectedDataTransform: "filters event markers by status",
      validation: "one or more known ledger statuses",
      risk: "medium",
      resetBehavior: "all statuses enabled"
    }),
    control({
      id: "eventType",
      label: "Event type",
      type: "chip-group",
      defaultValue: ["incident", "decision", "action", "evidence", "resolution"],
      options: ["incident", "decision", "action", "evidence", "resolution"].map((value) => ({ label: value, value })),
      affectedLayer: "timeline events",
      affectedDataTransform: "filters event markers by type",
      validation: "one or more known event types",
      risk: "medium",
      resetBehavior: "all event types enabled"
    }),
    control({
      id: "markerScale",
      label: "Marker scale",
      type: "range",
      defaultValue: 100,
      min: 70,
      max: 150,
      step: 5,
      affectedLayer: "marker geometry",
      affectedOptionPath: "series[1].data[].symbolSize / series[2].symbolSize",
      validation: "70-150",
      risk: "medium",
      resetBehavior: "100"
    }),
    control({
      id: "timelineDetail",
      label: "Detail",
      type: "segmented",
      defaultValue: "standard",
      options: [
        { label: "Calm", value: "calm-night" },
        { label: "Standard", value: "standard" },
        { label: "Forensic", value: "forensic" }
      ],
      affectedLayer: "labels/tooltips",
      affectedOptionPath: "series[1].label / tooltip",
      validation: "calm, standard, forensic",
      risk: "low",
      resetBehavior: "standard"
    }),
    control({
      id: "healthCurve",
      label: "Health curve",
      type: "segmented",
      defaultValue: "smooth",
      options: [
        { label: "Sharp", value: "sharp" },
        { label: "Smooth", value: "smooth" },
        { label: "Glass", value: "glass" }
      ],
      affectedLayer: "health line",
      affectedOptionPath: "series[0].smooth / series[0].areaStyle",
      validation: "sharp, smooth, glass",
      risk: "low",
      resetBehavior: "smooth"
    }),
    control({
      id: "eventPulse",
      label: "Event pulse",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "motion emphasis",
      affectedOptionPath: "series[2].data",
      validation: "boolean",
      risk: "low",
      resetBehavior: "enabled"
    }),
    control({
      id: "riskBand",
      label: "Risk bands",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "timeline background",
      affectedOptionPath: "series[0].markArea.data",
      validation: "boolean",
      risk: "low",
      resetBehavior: "enabled"
    }),
    control({
      id: "timeWindow",
      label: "Time window",
      type: "segmented",
      defaultValue: "all",
      options: [
        { label: "All", value: "all" },
        { label: "First", value: "first" },
        { label: "Recent", value: "recent" }
      ],
      affectedLayer: "viewport",
      affectedOptionPath: "dataZoom[].start / dataZoom[].end",
      validation: "all, first, recent",
      risk: "low",
      resetBehavior: "all"
    })
  ]),
  "pc.financial-operational-waterfall": commonChartControls([
    control({
      id: "moneyScale",
      label: "Money scale",
      type: "range",
      defaultValue: 100,
      min: 50,
      max: 150,
      step: 5,
      affectedLayer: "waterfall values",
      affectedDataTransform: "scales operational money impact for stress testing",
      validation: "50-150",
      risk: "medium",
      resetBehavior: "100"
    })
  ]),
  "tablet.shift-pulse-strip": commonChartControls([
    control({
      id: "queueFloor",
      label: "Queue floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 80,
      step: 5,
      affectedLayer: "shift buckets",
      affectedDataTransform: "filters low-pressure buckets",
      validation: "0-80",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "tablet.sync-outbox-status-matrix": commonChartControls([
    control({
      id: "syncState",
      label: "Sync state",
      type: "select",
      defaultValue: "all",
      options: [
        { label: "All", value: "all" },
        { label: "Pending", value: "pending" },
        { label: "Failed", value: "failed" },
        { label: "Retrying", value: "retrying" },
        { label: "Sent", value: "sent" }
      ],
      affectedLayer: "matrix columns",
      affectedDataTransform: "filters matrix cells by sync state",
      validation: "known sync state or all",
      risk: "medium",
      resetBehavior: "all"
    }),
    control({
      id: "blockingOnly",
      label: "Blocking only",
      type: "toggle",
      defaultValue: false,
      affectedLayer: "matrix cells",
      affectedDataTransform: "keeps only blocking cells",
      validation: "boolean",
      risk: "medium",
      resetBehavior: "off"
    })
  ]),
  "mobile.owner-pulse-timeline": commonChartControls([
    control({
      id: "healthFloor",
      label: "Health floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "timeline",
      affectedDataTransform: "filters points below health floor",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "mobile.action-inbox-priority-stack": commonChartControls([
    control({
      id: "ownerSearch",
      label: "Owner search",
      type: "search",
      defaultValue: "",
      affectedLayer: "owner stack",
      affectedDataTransform: "filters owner rows by text",
      validation: "plain text",
      risk: "low",
      resetBehavior: "empty"
    })
  ]),
  "mobile.health-radar-compact": commonChartControls([
    control({
      id: "radarFill",
      label: "Radar fill",
      type: "range",
      defaultValue: 18,
      min: 0,
      max: 45,
      step: 1,
      affectedLayer: "radar area",
      affectedOptionPath: "series[0].data[0].areaStyle.opacity",
      validation: "0-45",
      risk: "medium",
      resetBehavior: "18"
    })
  ]),
  "mobile.freshness-beacon-grid": commonChartControls([
    control({
      id: "freshnessFloor",
      label: "Freshness floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "freshness beacons",
      affectedDataTransform: "filters low freshness scores",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "mobile.incident-spark-cards": commonChartControls([
    control({
      id: "sparkSmoothing",
      label: "Spark smoothing",
      type: "toggle",
      defaultValue: true,
      affectedLayer: "line shape",
      affectedOptionPath: "series[0].smooth",
      validation: "boolean",
      risk: "low",
      resetBehavior: "on"
    })
  ]),
  "mobile.confidence-meter-bands": commonChartControls([
    control({
      id: "bandFloor",
      label: "Band floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "confidence bands",
      affectedDataTransform: "filters bands below confidence",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "pc.tablet-catalog-freshness-grid": commonChartControls([
    control({
      id: "freshnessFloor",
      label: "Freshness floor",
      type: "range",
      defaultValue: 0,
      min: 0,
      max: 100,
      step: 5,
      affectedLayer: "catalog freshness cells",
      affectedDataTransform: "filters low freshness scores in lab preview only",
      validation: "0-100",
      risk: "medium",
      resetBehavior: "0"
    })
  ]),
  "pc.sync-command-lifecycle-timeline": commonChartControls([
    control({
      id: "statusFocus",
      label: "Status focus",
      type: "select",
      defaultValue: "all",
      options: [
        { label: "All", value: "all" },
        { label: "Applied", value: "applied" },
        { label: "Rejected", value: "rejected" },
        { label: "Conflicted", value: "conflicted" },
        { label: "Duplicated", value: "duplicated" }
      ],
      affectedLayer: "lifecycle events",
      affectedDataTransform: "keeps visible events for selected lifecycle status in lab preview only",
      validation: "known lifecycle status or all",
      risk: "medium",
      resetBehavior: "all"
    })
  ]),
  "example.future-chart": [
    control({
      id: "disabledPlaceholder",
      label: "Placeholder controls",
      type: "toggle",
      defaultValue: false,
      affectedLayer: "none",
      validation: "disabled until chart 15 is promoted into a real option builder",
      risk: "low",
      resetBehavior: "off",
      disabledReason: "Example chart is visual scaffolding only."
    })
  ]
};

export function getControlsForChart(chartId: string): LabChartRuntimeControl[] {
  return chartControlSchemas[chartId] ?? [];
}

export function getDefaultControlState(chartId: string): LabChartControlState {
  return Object.fromEntries(getControlsForChart(chartId).map((item) => [item.id, item.defaultValue]));
}

export function countActiveControls(chartId: string, values: LabChartControlState): number {
  return getControlsForChart(chartId).filter((controlDef) => {
    const current = values[controlDef.id] ?? controlDef.defaultValue;
    return JSON.stringify(current) !== JSON.stringify(controlDef.defaultValue);
  }).length;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function seriesArray(option: Record<string, unknown>): Record<string, unknown>[] {
  const series = option.series;
  if (Array.isArray(series)) return series.filter(isRecord);
  if (isRecord(series)) return [series];
  return [];
}

function numeric(value: LabChartControlValue | undefined, fallback: number): number {
  return typeof value === "number" ? value : fallback;
}

function stringValue(value: LabChartControlValue | undefined, fallback: string): string {
  return typeof value === "string" ? value : fallback;
}

function booleanValue(value: LabChartControlValue | undefined, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function stringList(value: LabChartControlValue | undefined, fallback: string[]): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : fallback;
}

function scenarioMultiplier(scenario: LabChartScenario): number {
  if (scenario === "critical") return 1.24;
  if (scenario === "partial") return 0.68;
  if (scenario === "stale") return 0.82;
  if (scenario === "offline") return 0;
  if (scenario === "dense") return 1.1;
  return 1;
}

function scaleDatum(value: unknown, multiplier: number): unknown {
  if (typeof value === "number") return Math.max(0, Math.round(value * multiplier));
  if (Array.isArray(value)) {
    const next = [...value];
    let scaleIndex = -1;
    for (let index = next.length - 1; index > 1; index -= 1) {
      if (typeof next[index] === "number") {
        scaleIndex = index;
        break;
      }
    }
    if (scaleIndex >= 0) next[scaleIndex] = scaleDatum(next[scaleIndex], multiplier);
    return next;
  }
  if (isRecord(value)) {
    if (typeof value.value === "number") value.value = scaleDatum(value.value, multiplier);
    if (Array.isArray(value.value)) value.value = scaleDatum(value.value, multiplier);
    if (typeof value.symbolSize === "number") value.symbolSize = Math.max(4, Math.round(value.symbolSize * Math.min(1.25, multiplier || 0.4)));
    return value;
  }
  return value;
}

function applyScenario(option: Record<string, unknown>, scenario: LabChartScenario): void {
  const multiplier = scenarioMultiplier(scenario);
  for (const series of seriesArray(option)) {
    if (Array.isArray(series.data)) {
      series.data = series.data.map((item) => scaleDatum(item, multiplier));
    }
    if (Array.isArray(series.links)) {
      series.links = series.links.map((item) => scaleDatum(item, multiplier));
    }
  }
  const title = option.title;
  if (isRecord(title)) {
    title.subtext = `${String(title.subtext ?? "")} | scenario=${scenario} mock/demo`;
  }
}

function applyThemePreset(option: Record<string, unknown>, themePreset: LabChartThemePreset): void {
  const palette: Record<LabChartThemePreset, string[]> = {
    "crystal-light": ["#086dff", "#63dfff", "#13b981", "#e59b2a", "#df3d2f", "#7557ff"],
    "executive-dense": ["#0f172a", "#2563eb", "#0d9488", "#ca8a04", "#be123c", "#6d28d9"],
    forensic: ["#111827", "#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"],
    "high-contrast": ["#000000", "#005fcc", "#008a00", "#c05a00", "#d10000", "#5900cc"]
  };
  option.color = palette[themePreset];
  if (themePreset === "high-contrast") option.backgroundColor = "#ffffff";
}

function applySeriesLabels(option: Record<string, unknown>, show: boolean): void {
  for (const series of seriesArray(option)) {
    const label = isRecord(series.label) ? series.label : {};
    label.show = show;
    series.label = label;
  }
}

function applyVisualIntensity(option: Record<string, unknown>, intensity: number): void {
  const normalized = Math.max(0, Math.min(2, intensity / 100));
  const opacity = Math.max(0.18, Math.min(1, 0.38 + normalized * 0.44));
  const widthBoost = Math.max(1, Math.round(1 + normalized * 4));
  for (const series of seriesArray(option)) {
    const itemStyle = isRecord(series.itemStyle) ? series.itemStyle : {};
    itemStyle.opacity = opacity;
    if (normalized > 1.35) itemStyle.shadowBlur = Math.max(Number(itemStyle.shadowBlur ?? 0), Math.round((normalized - 1) * 12));
    series.itemStyle = itemStyle;
    const lineStyle = isRecord(series.lineStyle) ? series.lineStyle : {};
    if (Object.keys(lineStyle).length > 0) {
      lineStyle.width = widthBoost;
      lineStyle.opacity = Math.max(Number(lineStyle.opacity ?? 0.55), opacity);
    }
    series.lineStyle = lineStyle;
  }
}

function applyPowerStudioAtmosphere(option: Record<string, unknown>, values: LabChartControlState): void {
  const glowAura = numeric(values.glowAura, 8);
  const contrastPunch = numeric(values.contrastPunch, 72);
  const glowColor = contrastPunch > 145 ? "rgba(34, 211, 238, 0.32)" : "rgba(8, 109, 255, 0.18)";
  const borderWidth = contrastPunch > 160 ? 2 : contrastPunch > 100 ? 1 : 0;
  for (const series of seriesArray(option)) {
    const itemStyle = isRecord(series.itemStyle) ? series.itemStyle : {};
    itemStyle.shadowBlur = Math.max(Number(itemStyle.shadowBlur ?? 0), glowAura);
    itemStyle.shadowColor = glowColor;
    if (borderWidth > 0) itemStyle.borderWidth = Math.max(Number(itemStyle.borderWidth ?? 0), borderWidth);
    series.itemStyle = itemStyle;

    const lineStyle = isRecord(series.lineStyle) ? series.lineStyle : {};
    if (Object.keys(lineStyle).length > 0 || glowAura > 0) {
      lineStyle.shadowBlur = Math.max(Number(lineStyle.shadowBlur ?? 0), Math.round(glowAura * 0.72));
      lineStyle.shadowColor = glowColor;
      lineStyle.opacity = Math.max(Number(lineStyle.opacity ?? 0.48), Math.min(1, 0.32 + contrastPunch / 210));
      series.lineStyle = lineStyle;
    }

    const emphasis = isRecord(series.emphasis) ? series.emphasis : {};
    const emphasisItemStyle = isRecord(emphasis.itemStyle) ? emphasis.itemStyle : {};
    emphasisItemStyle.shadowBlur = Math.max(Number(emphasisItemStyle.shadowBlur ?? 0), glowAura + Math.round(contrastPunch / 12));
    emphasis.itemStyle = emphasisItemStyle;
    series.emphasis = emphasis;
  }
}

function applyMotionDirector(option: Record<string, unknown>, values: LabChartControlState, reducedMotion: boolean): void {
  const motionPreset = stringValue(values.motionPreset, "subtle-premium");
  const still = reducedMotion || motionPreset === "still" || !booleanValue(values.animation, true);
  const entranceDuration = still ? 0 : numeric(values.entranceDuration, motionPreset === "executive-snap" ? 420 : 900);
  const updateDuration = still ? 0 : numeric(values.updateDuration, motionPreset === "pulse-alerts" ? 1400 : 900);
  const staggerDelay = still ? 0 : numeric(values.staggerDelay, motionPreset === "sweep-scan" ? 38 : 20);
  const easingCurve = still ? "linear" : stringValue(values.easingCurve, motionPreset === "pulse-alerts" ? "elasticOut" : "cubicOut");
  option.animation = !still;
  option.animationDuration = entranceDuration;
  option.animationDurationUpdate = updateDuration;
  option.animationEasing = easingCurve;
  option.animationEasingUpdate = easingCurve;
  if (!still && staggerDelay > 0) {
    option.animationDelay = (index: number) => Math.min(1500, index * staggerDelay);
    option.animationDelayUpdate = (index: number) => Math.min(1500, index * Math.max(8, Math.round(staggerDelay / 2)));
  }
  for (const series of seriesArray(option)) {
    if (motionPreset === "sweep-scan" || motionPreset === "executive-snap") series.universalTransition = motionPreset === "sweep-scan";
  }
}

function applyInteractionStudio(option: Record<string, unknown>, values: LabChartControlState): void {
  const tooltipMode = stringValue(values.tooltipMode, "rich");
  const hoverSpotlight = stringValue(values.hoverSpotlight, "soft");

  if (tooltipMode === "none") {
    option.tooltip = { show: false };
  } else {
    const currentTooltip = isRecord(option.tooltip) ? option.tooltip : {};
    option.tooltip = {
      ...currentTooltip,
      show: true,
      trigger: currentTooltip.trigger ?? "item",
      confine: true,
      backgroundColor: tooltipMode === "forensic" ? "rgba(8, 15, 28, 0.94)" : "rgba(255, 255, 255, 0.94)",
      borderColor: tooltipMode === "forensic" ? "rgba(34, 211, 238, 0.42)" : "rgba(8, 109, 255, 0.24)",
      textStyle: { color: tooltipMode === "forensic" ? "#eff6ff" : "#071426", fontWeight: tooltipMode === "simple" ? 600 : 700 }
    };
  }

  for (const series of seriesArray(option)) {
    if (hoverSpotlight === "off") continue;
    const emphasis = isRecord(series.emphasis) ? series.emphasis : {};
    emphasis.focus = "series";
    series.emphasis = emphasis;
    const blur = isRecord(series.blur) ? series.blur : {};
    const blurItemStyle = isRecord(blur.itemStyle) ? blur.itemStyle : {};
    blurItemStyle.opacity = hoverSpotlight === "strong" ? 0.12 : 0.34;
    blur.itemStyle = blurItemStyle;
    series.blur = blur;
  }
}

function datumConfidence(item: unknown): number | null {
  if (isRecord(item) && typeof item.confidence === "number") return item.confidence;
  if (isRecord(item) && isRecord(item.item) && typeof item.item.confidence === "number") return item.item.confidence;
  if (Array.isArray(item)) {
    for (const part of item) {
      if (isRecord(part) && typeof part.confidence === "number") return part.confidence;
    }
  }
  return null;
}

function filterByConfidence(option: Record<string, unknown>, floor: number): void {
  if (floor <= 0) return;
  for (const series of seriesArray(option)) {
    if (Array.isArray(series.data)) series.data = series.data.filter((item) => (datumConfidence(item) ?? 100) >= floor);
    if (Array.isArray(series.links)) series.links = series.links.filter((item) => (datumConfidence(item) ?? 100) >= floor);
  }
}


// PRISMA_CAUSAL_FLOW_PREMIUM_PATCH_V2: visible forensic/evidence styling without changing chart contracts.
function causalSeverityColor(severity: string): string {
  if (severity === "CRITICAL") return "#df3d2f";
  if (severity === "ERROR") return "#ff6b3d";
  if (severity === "WARN") return "#e59b2a";
  return "#086dff";
}

function applyCausalControls(option: Record<string, unknown>, values: LabChartControlState): void {
  const series = seriesArray(option)[0];
  if (!series) return;
  const severities = stringList(values.severityFilter, ["INFO", "WARN", "ERROR", "CRITICAL"]);
  const confidenceFloor = numeric(values.confidenceFloor, 0);
  const stageFocus = stringValue(values.stageFocus, "all");
  const opacity = numeric(values.ribbonOpacity, 46) / 100;
  const layoutDensity = stringValue(values.layoutDensity, "balanced");
  const detailLevel = stringValue(values.detailLevel, "standard");
  const evidenceMode = booleanValue(values.evidenceMode, true);

  const existingLinks = series.links;
  if (Array.isArray(existingLinks)) {
    const filteredLinks = existingLinks
      .filter((link) => isRecord(link) && isRecord(link.item))
      .filter((link) => severities.includes(String((link as Record<string, Record<string, unknown>>).item.severity ?? "")))
      .filter((link) => Number((link as Record<string, Record<string, unknown>>).item.confidence ?? 100) >= confidenceFloor)
      .filter((link) => {
        if (stageFocus === "all") return true;
        const item = (link as Record<string, Record<string, unknown>>).item;
        return Boolean(item[stageFocus]);
      })
      .map((link) => {
        const record = link as Record<string, unknown>;
        const item = isRecord(record.item) ? record.item : {};
        const severity = String(item.severity ?? "INFO");
        const confidence = Number(item.confidence ?? 100);
        const color = causalSeverityColor(severity);
        const forensicMode = detailLevel === "forensic";
        const lineStyle = isRecord(record.lineStyle) ? record.lineStyle : {};
        lineStyle.opacity = opacity;
        lineStyle.color = color;
        lineStyle.shadowBlur = evidenceMode || forensicMode ? Math.max(4, Math.round(confidence / 10)) : 0;
        lineStyle.shadowColor = color;
        record.lineStyle = lineStyle;
        record.label = evidenceMode && forensicMode ? {
          show: true,
          formatter: `${severity} · ${confidence}%`,
          color: "#071426",
          fontSize: 10,
          fontWeight: 800,
          backgroundColor: "rgba(255, 255, 255, 0.78)",
          borderRadius: 8,
          padding: [2, 6]
        } : { show: false };
        return record;
      });
    series.links = filteredLinks;

    const usedNames = new Set<string>();
    for (const link of filteredLinks) {
      if (isRecord(link)) {
        if (typeof link.source === "string") usedNames.add(link.source);
        if (typeof link.target === "string") usedNames.add(link.target);
      }
    }
    if (Array.isArray(series.data)) {
      series.data = series.data.filter((node) => isRecord(node) && typeof node.name === "string" && usedNames.has(node.name));
    }
  }

  series.nodeWidth = numeric(values.ribbonWidth, 14);
  series.nodeGap = layoutDensity === "airy" ? 20 : layoutDensity === "dense" ? 7 : 12;
  series.layoutIterations = layoutDensity === "dense" ? 18 : layoutDensity === "airy" ? 44 : 32;
  const edgeLabel = isRecord(series.edgeLabel) ? series.edgeLabel : {};
  edgeLabel.show = evidenceMode && detailLevel === "forensic";
  edgeLabel.color = "#071426";
  edgeLabel.fontSize = 10;
  edgeLabel.fontWeight = 800;
  edgeLabel.backgroundColor = "rgba(255, 255, 255, 0.74)";
  edgeLabel.borderColor = "rgba(8, 109, 255, 0.16)";
  edgeLabel.borderWidth = 1;
  edgeLabel.borderRadius = 8;
  edgeLabel.padding = [2, 5];
  series.edgeLabel = edgeLabel;
}

function filterNumericSeriesData(option: Record<string, unknown>, floor: number): void {
  if (floor <= 0) return;
  for (const series of seriesArray(option)) {
    if (!Array.isArray(series.data)) continue;
    series.data = series.data.filter((item) => {
      if (typeof item === "number") return item >= floor;
      if (Array.isArray(item)) return item.some((part) => typeof part === "number" && part >= floor);
      if (isRecord(item) && typeof item.value === "number") return item.value >= floor;
      return true;
    });
  }
}


function numericDatumValue(item: unknown): number | null {
  if (typeof item === "number" && Number.isFinite(item)) return item;
  if (Array.isArray(item)) {
    for (let index = item.length - 1; index >= 0; index -= 1) {
      const part = item[index];
      if (typeof part === "number" && Number.isFinite(part)) return part;
    }
  }
  if (isRecord(item) && typeof item.value === "number" && Number.isFinite(item.value)) return item.value;
  if (isRecord(item) && Array.isArray(item.value)) return numericDatumValue(item.value);
  return null;
}

function filterCategoryAxisByIndexes(option: Record<string, unknown>, keepIndexes: Set<number>): void {
  const xAxis = option.xAxis;
  const axes = Array.isArray(xAxis) ? xAxis.filter(isRecord) : isRecord(xAxis) ? [xAxis] : [];
  for (const axis of axes) {
    if (Array.isArray(axis.data)) axis.data = axis.data.filter((_, index) => keepIndexes.has(index));
  }
}

function applyShiftPulseControls(option: Record<string, unknown>, values: LabChartControlState): void {
  const floor = numeric(values.queueFloor, 0);
  if (floor <= 0) return;
  const series = seriesArray(option);
  const queueSeries = series.find((item) => item.name === "Queue pressure") ?? series[0];
  const queueData = Array.isArray(queueSeries?.data) ? queueSeries.data : [];
  const keepIndexes = new Set<number>();
  queueData.forEach((item, index) => {
    const value = numericDatumValue(item);
    if ((value ?? 0) >= floor) keepIndexes.add(index);
  });
  filterCategoryAxisByIndexes(option, keepIndexes);
  for (const item of series) {
    if (Array.isArray(item.data) && item.data.length === queueData.length) {
      item.data = item.data.filter((_, index) => keepIndexes.has(index));
    }
  }
}



// PRISMA_DECISION_LEDGER_CONTROL_APPLY_V1: runtime control logic for Decision Ledger without breaking common knobs.
function decisionLedgerDatumNumber(item: unknown, key: string, fallback = 0): number {
  if (isRecord(item) && typeof item[key] === "number") return Number(item[key]);
  if (isRecord(item) && Array.isArray(item.value) && typeof item.value[1] === "number") return Number(item.value[1]);
  return fallback;
}

function decisionLedgerDatumString(item: unknown, key: string, fallback = ""): string {
  if (isRecord(item) && typeof item[key] === "string") return String(item[key]);
  return fallback;
}

function setDataZoomWindow(option: Record<string, unknown>, timeWindow: string): void {
  const zoom = option.dataZoom;
  const ranges: Record<string, [number, number]> = {
    all: [0, 100],
    first: [0, 58],
    recent: [42, 100]
  };
  const [start, end] = ranges[timeWindow] ?? ranges.all;
  if (!Array.isArray(zoom)) return;
  for (const item of zoom) {
    if (!isRecord(item)) continue;
    item.start = start;
    item.end = end;
  }
}

function applyDecisionLedgerControls(option: Record<string, unknown>, values: LabChartControlState): void {
  const impactFloor = numeric(values.impactFloor, 0);
  const confidenceFloor = numeric(values.confidenceFloor, 0);
  const evidenceFloor = numeric(values.evidenceFloor, 0);
  const markerScale = numeric(values.markerScale, 100) / 100;
  const timelineDetail = stringValue(values.timelineDetail, "standard");
  const healthCurve = stringValue(values.healthCurve, "smooth");
  const showPulse = booleanValue(values.eventPulse, true);
  const showRiskBand = booleanValue(values.riskBand, true);
  const statuses = stringList(values.ledgerStatus, ["open", "in_progress", "resolved", "blocked"]);
  const eventTypes = stringList(values.eventType, ["incident", "decision", "action", "evidence", "resolution"]);

  setDataZoomWindow(option, stringValue(values.timeWindow, "all"));

  for (const series of seriesArray(option)) {
    const name = String(series.name ?? "");

    if (name === "Health score") {
      series.smooth = healthCurve === "sharp" ? false : healthCurve === "glass" ? 0.58 : 0.36;
      const lineStyle = isRecord(series.lineStyle) ? series.lineStyle : {};
      lineStyle.width = healthCurve === "glass" ? 4 : healthCurve === "sharp" ? 2 : 3;
      lineStyle.shadowBlur = healthCurve === "glass" ? 20 : 10;
      series.lineStyle = lineStyle;
      const areaStyle = isRecord(series.areaStyle) ? series.areaStyle : {};
      areaStyle.opacity = healthCurve === "sharp" ? 0.04 : healthCurve === "glass" ? 0.32 : 0.16;
      series.areaStyle = areaStyle;
      if (!showRiskBand && isRecord(series.markArea)) series.markArea.data = [];
      continue;
    }

    if (name !== "Ledger events" && name !== "Event pulse") continue;

    if (name === "Event pulse" && !showPulse) {
      series.data = [];
      continue;
    }

    if (Array.isArray(series.data)) {
      series.data = series.data
        .filter((item) => decisionLedgerDatumNumber(item, "impactScore", 0) >= impactFloor)
        .filter((item) => decisionLedgerDatumNumber(item, "confidence", 100) >= confidenceFloor)
        .filter((item) => decisionLedgerDatumNumber(item, "evidenceCount", 0) >= evidenceFloor)
        .filter((item) => statuses.includes(decisionLedgerDatumString(item, "status", "open")))
        .filter((item) => eventTypes.includes(decisionLedgerDatumString(item, "type", "decision")))
        .map((item) => {
          if (!isRecord(item)) return item;
          const current = typeof item.symbolSize === "number" ? item.symbolSize : 22;
          item.symbolSize = Math.max(8, Math.round(current * markerScale));
          return item;
        });
    }

    const label = isRecord(series.label) ? series.label : {};
    label.show = timelineDetail !== "calm" && name === "Ledger events";
    label.fontSize = timelineDetail === "forensic" ? 11 : 10;
    label.distance = timelineDetail === "forensic" ? 12 : 8;
    series.label = label;

    if (name === "Event pulse") {
      series.symbolSize = Math.max(20, Math.round(34 * markerScale));
      const rippleEffect = isRecord(series.rippleEffect) ? series.rippleEffect : {};
      rippleEffect.scale = timelineDetail === "forensic" ? 3 : 2.35;
      rippleEffect.number = timelineDetail === "forensic" ? 4 : 2;
      series.rippleEffect = rippleEffect;
    }
  }
}



// PRISMA_RADICAL_THEME_RUNTIME_V1
// Mutates ECharts options from Runtime Controls so themePreset is a rendering engine, not a paint bucket.
type PrismaRadicalThemeId = "crystal-light" | "paper" | "calm-night" | "dense-noir";

type PrismaRadicalTheme = {
  id: PrismaRadicalThemeId;
  mode: "light" | "dark";
  textPrimary: string;
  textMuted: string;
  grid: string;
  axis: string;
  accent: string;
  accent2: string;
  accent3: string;
  line: string;
  areaTop: string;
  areaBottom: string;
  pulse: string;
  statusOpen: string;
  statusResolved: string;
  statusProgress: string;
  statusBlocked: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
  zoomBg: string;
  zoomFill: string;
  zoomHandle: string;
  labelBg: string;
  labelBorder: string;
  radiusMd: number;
  lineWidth: number;
  smooth: number | boolean;
  labelDensity: "full" | "short" | "quiet" | "minimal";
  rippleScale: number;
  rippleNumber: number;
  shadowBlur: number;
  glow: string;
};

const PRISMA_RADICAL_THEMES: Record<PrismaRadicalThemeId, PrismaRadicalTheme> = {
  "crystal-light": {
    id: "crystal-light", mode: "light", textPrimary: "#0a1830", textMuted: "#6a7a92", grid: "rgba(77,120,170,0.12)", axis: "rgba(77,120,170,0.22)", accent: "#0b78ff", accent2: "#63dfff", accent3: "#7557ff", line: "#63dfff", areaTop: "rgba(99,223,255,0.26)", areaBottom: "rgba(99,223,255,0.02)", pulse: "rgba(99,223,255,0.26)", statusOpen: "#e59b2a", statusResolved: "#13b981", statusProgress: "#7557ff", statusBlocked: "#df3d2f", tooltipBg: "rgba(255,255,255,0.94)", tooltipBorder: "rgba(99,223,255,0.26)", tooltipText: "#071426", zoomBg: "rgba(255,255,255,0.38)", zoomFill: "rgba(8,109,255,0.16)", zoomHandle: "#ffffff", labelBg: "rgba(255,255,255,0.76)", labelBorder: "rgba(99,223,255,0.20)", radiusMd: 14, lineWidth: 3, smooth: 0.42, labelDensity: "full", rippleScale: 2.6, rippleNumber: 3, shadowBlur: 16, glow: "rgba(99,223,255,0.34)"
  },
  paper: {
    id: "paper", mode: "light", textPrimary: "#2b2115", textMuted: "#8b7a67", grid: "rgba(92,73,44,0.10)", axis: "rgba(92,73,44,0.20)", accent: "#8f5f2d", accent2: "#c9a46a", accent3: "#6b5142", line: "#8f5f2d", areaTop: "rgba(201,164,106,0.24)", areaBottom: "rgba(201,164,106,0.02)", pulse: "rgba(143,95,45,0.16)", statusOpen: "#c47a1b", statusResolved: "#3f8b56", statusProgress: "#7c5db5", statusBlocked: "#b64533", tooltipBg: "rgba(255,251,246,0.96)", tooltipBorder: "rgba(140,112,70,0.18)", tooltipText: "#2b2115", zoomBg: "rgba(255,247,238,0.52)", zoomFill: "rgba(143,95,45,0.14)", zoomHandle: "#fff8f1", labelBg: "rgba(255,250,244,0.82)", labelBorder: "rgba(92,73,44,0.12)", radiusMd: 10, lineWidth: 2, smooth: 0.18, labelDensity: "short", rippleScale: 1.9, rippleNumber: 2, shadowBlur: 8, glow: "rgba(201,164,106,0.18)"
  },
  "calm-night": {
    id: "calm-night", mode: "dark", textPrimary: "#e7f0fb", textMuted: "#7e93ab", grid: "rgba(117,153,196,0.12)", axis: "rgba(117,153,196,0.18)", accent: "#40a9ff", accent2: "#38e1ff", accent3: "#61a0ff", line: "#38e1ff", areaTop: "rgba(56,225,255,0.18)", areaBottom: "rgba(56,225,255,0.01)", pulse: "rgba(56,225,255,0.22)", statusOpen: "#f3b45a", statusResolved: "#2ed39a", statusProgress: "#8e79ff", statusBlocked: "#ff6a63", tooltipBg: "rgba(14,20,33,0.96)", tooltipBorder: "rgba(56,225,255,0.20)", tooltipText: "#eef6ff", zoomBg: "rgba(26,40,60,0.82)", zoomFill: "rgba(64,169,255,0.18)", zoomHandle: "#d9e9f9", labelBg: "rgba(14,20,33,0.82)", labelBorder: "rgba(56,225,255,0.14)", radiusMd: 14, lineWidth: 3, smooth: 0.36, labelDensity: "quiet", rippleScale: 2.35, rippleNumber: 3, shadowBlur: 18, glow: "rgba(56,225,255,0.26)"
  },
  "dense-noir": {
    id: "dense-noir", mode: "dark", textPrimary: "#f7f8fb", textMuted: "#7e8698", grid: "rgba(145,153,181,0.10)", axis: "rgba(145,153,181,0.16)", accent: "#7557ff", accent2: "#29d3ff", accent3: "#ff4fd8", line: "#7557ff", areaTop: "rgba(117,87,255,0.22)", areaBottom: "rgba(117,87,255,0.01)", pulse: "rgba(117,87,255,0.22)", statusOpen: "#ffb44d", statusResolved: "#31d0a2", statusProgress: "#7557ff", statusBlocked: "#ff5c74", tooltipBg: "rgba(12,14,22,0.96)", tooltipBorder: "rgba(117,87,255,0.22)", tooltipText: "#f8fbff", zoomBg: "rgba(19,22,32,0.88)", zoomFill: "rgba(117,87,255,0.22)", zoomHandle: "#e4e7f1", labelBg: "rgba(12,14,22,0.76)", labelBorder: "rgba(117,87,255,0.16)", radiusMd: 10, lineWidth: 4, smooth: 0.52, labelDensity: "minimal", rippleScale: 3.15, rippleNumber: 4, shadowBlur: 24, glow: "rgba(117,87,255,0.30)"
  }
};

function prismaRadicalRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function prismaRadicalArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(prismaRadicalRecord(item))) : [];
}

function prismaRadicalThemeId(value: unknown): PrismaRadicalThemeId {
  const normalized = typeof value === "string" ? value.trim().toLowerCase().replace(/_/g, "-") : "crystal-light";
  if (normalized === "paper" || normalized === "editorial") return "paper";
  if (normalized === "calm" || normalized === "calm-night" || normalized === "night") return "calm-night";
  if (normalized === "dense" || normalized === "dense-noir" || normalized === "executive-dense" || normalized === "noir") return "dense-noir";
  return "crystal-light";
}

function prismaRadicalStatusColor(status: unknown, t: PrismaRadicalTheme): string {
  if (status === "resolved") return t.statusResolved;
  if (status === "blocked" || status === "failed") return t.statusBlocked;
  if (status === "in_progress") return t.statusProgress;
  return t.statusOpen;
}

function prismaRadicalPatchAxis(axis: unknown, t: PrismaRadicalTheme): void {
  const axes = Array.isArray(axis) ? axis : [axis];
  for (const raw of axes) {
    const item = prismaRadicalRecord(raw);
    if (!item) continue;
    item.axisLine = { ...(prismaRadicalRecord(item.axisLine) ?? {}), lineStyle: { color: t.axis } };
    item.axisLabel = { ...(prismaRadicalRecord(item.axisLabel) ?? {}), color: t.textMuted, fontWeight: 750 };
    item.nameTextStyle = { ...(prismaRadicalRecord(item.nameTextStyle) ?? {}), color: t.textMuted, fontWeight: 900 };
    item.splitLine = { ...(prismaRadicalRecord(item.splitLine) ?? {}), lineStyle: { color: t.grid, type: t.id === "paper" ? "solid" : "dashed" } };
  }
}

function applyRadicalThemeToOption(option: Record<string, unknown>, values: LabChartControlState): void {
  const themeId = prismaRadicalThemeId(values.themePreset ?? values.theme ?? values.themeMode);
  const t = PRISMA_RADICAL_THEMES[themeId];
  option.color = [t.accent, t.accent2, t.statusResolved, t.statusOpen, t.statusBlocked, t.accent3];
  option.backgroundColor = "transparent";
  option.textStyle = { ...(prismaRadicalRecord(option.textStyle) ?? {}), color: t.textPrimary };
  const title = prismaRadicalRecord(option.title);
  if (title) {
    title.textStyle = { ...(prismaRadicalRecord(title.textStyle) ?? {}), color: t.textPrimary, fontWeight: 900 };
    title.subtextStyle = { ...(prismaRadicalRecord(title.subtextStyle) ?? {}), color: t.textMuted, fontWeight: themeId === "paper" ? 650 : 800 };
  }
  const legend = prismaRadicalRecord(option.legend);
  if (legend) legend.textStyle = { ...(prismaRadicalRecord(legend.textStyle) ?? {}), color: t.textMuted, fontWeight: 800 };
  const tooltip = prismaRadicalRecord(option.tooltip);
  if (tooltip) {
    tooltip.backgroundColor = t.tooltipBg;
    tooltip.borderColor = t.tooltipBorder;
    tooltip.textStyle = { ...(prismaRadicalRecord(tooltip.textStyle) ?? {}), color: t.tooltipText };
    tooltip.extraCssText = `border-radius:${t.radiusMd}px;box-shadow:0 22px 70px rgba(0,0,0,${t.mode === "dark" ? ".34" : ".14"});backdrop-filter:blur(${themeId === "paper" ? "4" : "18"}px);`;
  }
  prismaRadicalPatchAxis(option.xAxis, t);
  prismaRadicalPatchAxis(option.yAxis, t);
  for (const zoom of prismaRadicalArray(option.dataZoom)) {
    zoom.backgroundColor = t.zoomBg;
    zoom.fillerColor = t.zoomFill;
    zoom.borderColor = t.axis;
    zoom.handleStyle = { ...(prismaRadicalRecord(zoom.handleStyle) ?? {}), color: t.zoomHandle, borderColor: t.accent, shadowBlur: t.shadowBlur, shadowColor: t.glow };
    zoom.textStyle = { ...(prismaRadicalRecord(zoom.textStyle) ?? {}), color: t.textMuted, fontWeight: 750 };
  }
  for (const series of prismaRadicalArray(option.series)) {
    const name = String(series.name ?? "").toLowerCase();
    if (name.includes("health") || series.type === "line") {
      series.smooth = t.smooth;
      series.lineStyle = { ...(prismaRadicalRecord(series.lineStyle) ?? {}), color: t.line, width: t.lineWidth, shadowBlur: t.shadowBlur, shadowColor: t.glow };
      series.areaStyle = { ...(prismaRadicalRecord(series.areaStyle) ?? {}), color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: t.areaTop }, { offset: 1, color: t.areaBottom }] } };
    }
    if (series.type === "scatter" || name.includes("ledger") || name.includes("event")) {
      const label = prismaRadicalRecord(series.label) ?? {};
      label.show = t.labelDensity !== "minimal" && label.show !== false;
      label.color = t.textPrimary;
      label.backgroundColor = t.labelBg;
      label.borderColor = t.labelBorder;
      label.borderRadius = t.radiusMd;
      label.fontWeight = themeId === "paper" ? 750 : 900;
      series.label = label;
      const data = Array.isArray(series.data) ? series.data : [];
      series.data = data.map((raw) => {
        const item = prismaRadicalRecord(raw);
        if (!item) return raw;
        const color = prismaRadicalStatusColor(item.status, t);
        item.itemStyle = { ...(prismaRadicalRecord(item.itemStyle) ?? {}), color, shadowColor: color, shadowBlur: t.shadowBlur };
        return item;
      });
    }
    if (series.type === "effectScatter" || name.includes("pulse")) {
      series.symbolSize = themeId === "dense-noir" ? 38 : themeId === "paper" ? 24 : 34;
      series.rippleEffect = { ...(prismaRadicalRecord(series.rippleEffect) ?? {}), number: t.rippleNumber, scale: t.rippleScale, brushType: "stroke" };
      series.itemStyle = { ...(prismaRadicalRecord(series.itemStyle) ?? {}), color: t.pulse, shadowBlur: t.shadowBlur, shadowColor: t.glow };
    }
  }
}

function applyChartSpecificControls(chartId: string, option: Record<string, unknown>, values: LabChartControlState): void {
  applyRadicalThemeToOption(option, values);
  switch (chartId) {
    case "pc.causal-flow-ribbon":
      applyCausalControls(option, values);
      break;
    case "pc.operational-density-field":
      filterNumericSeriesData(option, numeric(values.pressureFloor, 0));
      break;
    case "pc.service-dependency-graph": {
      const series = seriesArray(option)[0];
      if (series && isRecord(series.force)) series.force.repulsion = numeric(values.forceRepulsion, 210);
      break;
    }
    case "pc.inventory-risk-treemap": {
      const series = seriesArray(option)[0];
      if (series) series.leafDepth = stringValue(values.leafDepth, "category") === "sku" ? 2 : 1;
      break;
    }
    case "pc.decision-ledger-timeline":
      applyDecisionLedgerControls(option, values);
      break;
    case "pc.financial-operational-waterfall":
      applyScenario(option, numeric(values.moneyScale, 100) > 100 ? "critical" : "clean");
      break;
    case "tablet.shift-pulse-strip":
      applyShiftPulseControls(option, values);
      break;
    case "mobile.owner-pulse-timeline":
      filterNumericSeriesData(option, numeric(values.healthFloor, 0));
      break;
    case "mobile.health-radar-compact": {
      const firstSeries = seriesArray(option)[0];
      const data = Array.isArray(firstSeries?.data) ? firstSeries.data[0] : null;
      if (isRecord(data)) {
        const areaStyle = isRecord(data.areaStyle) ? data.areaStyle : {};
        areaStyle.opacity = numeric(values.radarFill, 18) / 100;
        data.areaStyle = areaStyle;
      }
      break;
    }
    case "mobile.freshness-beacon-grid":
      filterNumericSeriesData(option, numeric(values.freshnessFloor, 0));
      break;
    case "mobile.incident-spark-cards": {
      const firstSeries = seriesArray(option)[0];
      if (firstSeries) firstSeries.smooth = booleanValue(values.sparkSmoothing, true);
      break;
    }
    case "mobile.confidence-meter-bands":
      filterNumericSeriesData(option, numeric(values.bandFloor, 0));
      break;
    default:
      break;
  }
}

export function applyChartLabControls(input: {
  chartId: string;
  option: Record<string, unknown>;
  values: LabChartControlState;
  reducedMotion: boolean;
}): Record<string, unknown> {
  const scenario = stringValue(input.values.dataScenario, "clean") as LabChartScenario;
  const themePreset = stringValue(input.values.themePreset, "crystal-light") as LabChartThemePreset;
  applyScenario(input.option, scenario);
  applyThemePreset(input.option, themePreset);
  applySeriesLabels(input.option, booleanValue(input.values.showLabels, true));
  applyVisualIntensity(input.option, numeric(input.values.visualIntensity, 70));
  applyPowerStudioAtmosphere(input.option, input.values);
  filterByConfidence(input.option, numeric(input.values.confidenceFloor, 0));
  applyMotionDirector(input.option, input.values, input.reducedMotion);
  applyInteractionStudio(input.option, input.values);
  applyChartSpecificControls(input.chartId, input.option, input.values);
  return input.option;
}
