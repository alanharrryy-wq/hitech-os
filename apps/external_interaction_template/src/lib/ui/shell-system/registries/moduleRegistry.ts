import type { ModuleDescriptor } from "@/lib/ui/shell-system/types";
import { validateModules } from "@/lib/ui/shell-system/validators";

const rawModules: ModuleDescriptor[] = [
  {
    id: "launcher",
    labelKey: "shell.nav.launcher",
    routePrefix: "/",
    defaultArea: "launcher",
    navItemIds: ["launcher"],
    actionIds: ["start-flow", "open-schemas"],
    widgetIds: ["runtime-summary"],
    visibility: {},
    permissions: ["workspace.read"]
  },
  {
    id: "inbox",
    labelKey: "shell.nav.inbox",
    routePrefix: "/inbox",
    defaultArea: "inbox",
    navItemIds: ["inbox"],
    actionIds: ["start-flow"],
    widgetIds: ["quick-filters", "runtime-summary"],
    visibility: {},
    permissions: ["records.read"]
  },
  {
    id: "sync",
    labelKey: "shell.nav.sync",
    routePrefix: "/sync",
    defaultArea: "sync",
    navItemIds: ["sync"],
    actionIds: ["open-sync"],
    widgetIds: ["runtime-summary"],
    visibility: {},
    permissions: ["sync.read"]
  },
  {
    id: "schemas",
    labelKey: "shell.nav.schemas",
    routePrefix: "/playground",
    defaultArea: "system",
    navItemIds: ["schemas", "schemas-flows"],
    actionIds: ["open-schemas", "open-utilities"],
    widgetIds: ["plugin-tray"],
    visibility: {},
    permissions: ["schemas.read"]
  }
];

export const moduleRegistry = validateModules(rawModules);

