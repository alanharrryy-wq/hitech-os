import type { PrefabDefinition, SlotEntity } from "../authoring-workbench-contracts";

export const AUTHORING_WORKBENCH_PREFABS: readonly PrefabDefinition[] = [
  {
    id: "prefab-hero-text",
    title: "Hero Text",
    widgetType: "text",
    acceptedSlotKinds: ["content", "container"],
    acceptedCapabilities: ["textual"],
    defaultProps: {
      text: "Headline",
    },
    defaultStyle: {
      background: "rgba(255,255,255,0.12)",
      foreground: "#ffffff",
      borderStyle: "glass",
      radius: 16,
      emphasis: "strong",
    },
    description: "Large scene introduction text with glass treatment.",
    tags: ["text", "hero"],
  },
  {
    id: "prefab-kpi-card",
    title: "KPI Card",
    widgetType: "kpi",
    acceptedSlotKinds: ["metric", "content"],
    acceptedCapabilities: ["metric"],
    defaultProps: {
      label: "Metric",
      value: "0",
      delta: "+0%",
    },
    defaultStyle: {
      background: "rgba(10, 14, 28, 0.78)",
      foreground: "#ffffff",
      borderStyle: "solid",
      radius: 14,
      emphasis: "default",
    },
    description: "Single KPI with label, value, and delta.",
    tags: ["kpi", "metric"],
  },
  {
    id: "prefab-line-chart",
    title: "Line Chart",
    widgetType: "chart",
    acceptedSlotKinds: ["chart", "content"],
    acceptedCapabilities: ["chart"],
    defaultProps: {
      chartType: "line",
      title: "Line Chart",
      dataSetRef: "sample.series.default",
    },
    defaultStyle: {
      background: "rgba(255,255,255,0.08)",
      foreground: "#ffffff",
      borderStyle: "glass",
      radius: 18,
      emphasis: "default",
    },
    description: "Basic line chart with bounded styling defaults.",
    tags: ["chart", "trend"],
  },
];

export function getCompatiblePrefabs(slot: SlotEntity): readonly PrefabDefinition[] {
  return AUTHORING_WORKBENCH_PREFABS.filter((prefab) => {
    if (!prefab.acceptedSlotKinds.includes(slot.kind)) {
      return false;
    }
    if (slot.acceptedWidgetTypes.length > 0 && !slot.acceptedWidgetTypes.includes(prefab.widgetType)) {
      return false;
    }
    return prefab.acceptedCapabilities.some((capability) => slot.acceptedCapabilities.includes(capability));
  });
}

export function getPrefabById(prefabId: string): PrefabDefinition | null {
  return AUTHORING_WORKBENCH_PREFABS.find((prefab) => prefab.id === prefabId) ?? null;
}
