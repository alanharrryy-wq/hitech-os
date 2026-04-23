import type { WidgetDescriptor } from "@/lib/ui/shell-system/types";

export const CLIENT_WIDGETS: WidgetDescriptor[] = [
  {
    id: "runtime-summary",
    titleKey: "shell.widget.runtime.title",
    summaryKey: "shell.widget.runtime.summary",
    slot: "contextualPanelSlot",
    priority: 10,
    icon: {
      family: "system",
      name: "view"
    },
    visibility: {
      hideAreas: ["flow"],
      requiredPermissions: ["workspace.read"]
    },
    permissions: ["workspace.read"],
    componentId: "runtimeSummary",
    mobilePolicy: "drawer"
  },
  {
    id: "quick-filters",
    titleKey: "shell.widget.filters.title",
    summaryKey: "shell.widget.filters.summary",
    slot: "quickFiltersSlot",
    priority: 20,
    icon: {
      family: "system",
      name: "filter"
    },
    visibility: {
      whenAreas: ["inbox"],
      requiredPermissions: ["records.read"]
    },
    permissions: ["records.read"],
    componentId: "quickFilters",
    mobilePolicy: "drawer"
  },
  {
    id: "plugin-tray",
    titleKey: "shell.widget.plugins.title",
    summaryKey: "shell.widget.plugins.summary",
    slot: "pluginTraySlot",
    priority: 30,
    icon: {
      family: "system",
      name: "integration"
    },
    visibility: {
      requiredPermissions: ["utilities.open"]
    },
    permissions: ["utilities.open"],
    componentId: "pluginTray",
    mobilePolicy: "hide"
  }
];

