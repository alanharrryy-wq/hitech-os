import {
  WidgetCollection,
  WidgetCollectionSchema,
  WidgetConfig
} from "../mission-control/widgets.js";
import { parseOrThrow } from "../parsing.js";

export const WIDGET_FIXTURES: readonly WidgetConfig[] = [
  {
    id: "wid_table-001",
    kind: "table",
    title: "Active Runs",
    subtitle: "Execution queue",
    description: "Current run queue with owner and SLA.",
    refresh: { mode: "interval", intervalSeconds: 20 },
    density: "comfortable",
    pinned: true,
    hidden: false,
    config: {
      columns: [
        {
          key: "id",
          label: "Run ID",
          align: "left",
          width: 180,
          sortable: true,
          truncation: "line"
        },
        {
          key: "name",
          label: "Name",
          align: "left",
          width: 260,
          sortable: true,
          truncation: "line"
        },
        {
          key: "status",
          label: "Status",
          align: "center",
          width: 120,
          sortable: true,
          truncation: "none"
        },
        {
          key: "progress",
          label: "Progress",
          align: "right",
          width: 120,
          sortable: true,
          truncation: "none"
        }
      ],
      rowKey: "id",
      maxRows: 25,
      striped: true,
      stickyHeader: true
    }
  },
  {
    id: "wid_feed-001",
    kind: "feed",
    title: "Activity Feed",
    subtitle: "Latest events",
    description: "Near real-time activity timeline.",
    refresh: { mode: "interval", intervalSeconds: 10 },
    density: "comfortable",
    pinned: true,
    hidden: false,
    config: {
      source: "activity",
      maxItems: 40,
      showSeverity: true,
      compactTimestamps: true
    }
  },
  {
    id: "wid_stat-001",
    kind: "stat",
    title: "Runs In Flight",
    subtitle: "Current",
    description: null,
    refresh: { mode: "interval", intervalSeconds: 15 },
    density: "compact",
    pinned: true,
    hidden: false,
    config: {
      value: 6,
      unit: "runs",
      trend: "up",
      precision: 0,
      sparkline: [4, 5, 5, 6, 6, 6]
    }
  },
  {
    id: "wid_stat-002",
    kind: "stat",
    title: "Success Rate",
    subtitle: "24h",
    description: "Completion ratio for the last 24h.",
    refresh: { mode: "interval", intervalSeconds: 60 },
    density: "compact",
    pinned: false,
    hidden: false,
    config: {
      value: 93.2,
      unit: "%",
      trend: "flat",
      precision: 1,
      sparkline: [94, 93, 92, 94, 93.2]
    }
  },
  {
    id: "wid_chart-001",
    kind: "chart-placeholder",
    title: "CPU By Worker",
    subtitle: "Placeholder",
    description: "Placeholder chart until metrics adapter ships.",
    refresh: { mode: "manual", intervalSeconds: null },
    density: "comfortable",
    pinned: false,
    hidden: false,
    config: {
      chartFamily: "line",
      xLabel: "time",
      yLabel: "cpu%",
      seriesNames: ["worker-1", "worker-2", "worker-3"],
      supportsStacking: false
    }
  },
  {
    id: "wid_dial-001",
    kind: "dial-placeholder",
    title: "Queue Pressure",
    subtitle: "critical indicator",
    description: null,
    refresh: { mode: "interval", intervalSeconds: 5 },
    density: "compact",
    pinned: true,
    hidden: false,
    config: {
      min: 0,
      max: 100,
      value: 72,
      warningThreshold: 70,
      criticalThreshold: 90,
      unit: "%"
    }
  },
  {
    id: "wid_table-002",
    kind: "table",
    title: "Completed Runs",
    subtitle: "Historical",
    description: null,
    refresh: { mode: "passive", intervalSeconds: null },
    density: "comfortable",
    pinned: false,
    hidden: false,
    config: {
      columns: [
        { key: "id", label: "Run", align: "left", width: 180, sortable: true, truncation: "line" },
        {
          key: "endedAt",
          label: "Finished",
          align: "left",
          width: 180,
          sortable: true,
          truncation: "none"
        },
        {
          key: "duration",
          label: "Duration",
          align: "right",
          width: 120,
          sortable: true,
          truncation: "none"
        }
      ],
      rowKey: "id",
      maxRows: 100,
      striped: true,
      stickyHeader: true
    }
  },
  {
    id: "wid_feed-002",
    kind: "feed",
    title: "Alerts",
    subtitle: "System",
    description: "Critical and warning level alerts.",
    refresh: { mode: "interval", intervalSeconds: 8 },
    density: "compact",
    pinned: false,
    hidden: false,
    config: {
      source: "alerts",
      maxItems: 30,
      showSeverity: true,
      compactTimestamps: false
    }
  },
  {
    id: "wid_chart-002",
    kind: "chart-placeholder",
    title: "Latency Envelope",
    subtitle: "Placeholder",
    description: null,
    refresh: { mode: "manual", intervalSeconds: null },
    density: "spacious",
    pinned: false,
    hidden: false,
    config: {
      chartFamily: "area",
      xLabel: "minute",
      yLabel: "ms",
      seriesNames: ["p50", "p90", "p99"],
      supportsStacking: true
    }
  },
  {
    id: "wid_dial-002",
    kind: "dial-placeholder",
    title: "Index Freshness",
    subtitle: null,
    description: null,
    refresh: { mode: "interval", intervalSeconds: 12 },
    density: "compact",
    pinned: false,
    hidden: false,
    config: {
      min: 0,
      max: 100,
      value: 88,
      warningThreshold: 70,
      criticalThreshold: 50,
      unit: "%"
    }
  }
];

export const WIDGET_COLLECTION_FIXTURE: WidgetCollection = {
  version: 2,
  widgets: [...WIDGET_FIXTURES]
};

export function getWidgetFixtures(): readonly WidgetConfig[] {
  return WIDGET_FIXTURES;
}

export function parseWidgetFixtures(): readonly WidgetConfig[] {
  return WIDGET_FIXTURES.map((widget) =>
    parseOrThrow(WidgetCollectionSchema.shape.widgets.element, widget, {
      resource: "widget",
      operation: "fixture-parse"
    })
  );
}

export function parseWidgetCollectionFixture(): WidgetCollection {
  return parseOrThrow(WidgetCollectionSchema, WIDGET_COLLECTION_FIXTURE, {
    resource: "widgets",
    operation: "fixture-collection-parse"
  });
}
