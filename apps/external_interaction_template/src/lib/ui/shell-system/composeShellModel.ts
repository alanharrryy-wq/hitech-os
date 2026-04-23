import { CLIENT_ACTIONS } from "@/lib/ui/shell-system/client/client.actions";
import { CLIENT_MANIFEST } from "@/lib/ui/shell-system/client/client.manifest";
import { CLIENT_DEFAULT_PERMISSIONS } from "@/lib/ui/shell-system/client/client.permissions";
import { CLIENT_WIDGETS } from "@/lib/ui/shell-system/client/client.widgets";
import { moduleRegistry } from "@/lib/ui/shell-system/registries/moduleRegistry";
import { navRegistry } from "@/lib/ui/shell-system/registries/navRegistry";
import type {
  ActionSlotPayload,
  NavItemDescriptor,
  NavSlotPayload,
  ResolvedShellModel,
  ShellRuntimeContext,
  WidgetSlotPayload
} from "@/lib/ui/shell-system/types";
import {
  validateActionItems,
  validateActionSlot,
  validateBrandSlot,
  validateFooterSlot,
  validateModules,
  validateNavItems,
  validateNavSlot,
  validateWidgetItems,
  validateWidgetSlot,
  validateWorkspaceSlot
} from "@/lib/ui/shell-system/validators";
import { filterVisibleActions, filterVisibleNavItems, filterVisibleWidgets, isVisibleByPolicy } from "@/lib/ui/shell-system/visibility";

function sortByPriority<T extends { priority: number }>(items: readonly T[]): T[] {
  return [...items].sort((left, right) => left.priority - right.priority);
}

function baseSlotConfig() {
  return {
    visibility: {},
    slotVisibility: {
      desktop: "show",
      tablet: "show",
      mobile: "show"
    },
    emptyBehavior: "collapse",
    breakpoints: {
      desktop: "expanded",
      tablet: "compact",
      mobile: "drawer"
    }
  } as const;
}

function resolveActiveModules(context: ShellRuntimeContext): string[] {
  return validateModules(moduleRegistry)
    .filter((module) => isVisibleByPolicy(module.visibility, context))
    .filter((module) => module.permissions.every((permission) => context.permissions.has(permission)))
    .filter((module) => context.currentPath === module.routePrefix || context.currentPath.startsWith(`${module.routePrefix}/`))
    .map((module) => module.id);
}

function filterByModules<T extends { id: string }>(
  items: T[],
  activeModules: string[],
  resolver: (moduleId: string) => readonly string[]
): T[] {
  if (activeModules.length === 0) return items;
  const allowedIds = new Set<string>();
  for (const moduleId of activeModules) {
    for (const id of resolver(moduleId)) {
      allowedIds.add(id);
    }
  }
  return items.filter((item) => allowedIds.has(item.id));
}

function navSlotPayload(slotId: NavSlotPayload["slotId"], items: NavItemDescriptor[]): NavSlotPayload | undefined {
  const validatedItems = validateNavItems(items);
  if (validatedItems.length === 0) return undefined;
  return validateNavSlot({
    slotId,
    items: validatedItems,
    ...baseSlotConfig()
  });
}

function actionSlotPayload(slotId: ActionSlotPayload["slotId"], items: ActionSlotPayload["items"]): ActionSlotPayload | undefined {
  const validatedItems = validateActionItems(items);
  if (validatedItems.length === 0) return undefined;
  return validateActionSlot({
    slotId,
    items: validatedItems,
    ...baseSlotConfig()
  });
}

function widgetSlotPayload(slotId: WidgetSlotPayload["slotId"], widgets: WidgetSlotPayload["widgets"]): WidgetSlotPayload | undefined {
  const validatedWidgets = validateWidgetItems(widgets);
  if (validatedWidgets.length === 0) return undefined;
  return validateWidgetSlot({
    slotId,
    widgets: validatedWidgets,
    ...baseSlotConfig()
  });
}

export function createShellPermissionsSet(permissions = CLIENT_DEFAULT_PERMISSIONS): Set<string> {
  return new Set(permissions);
}

export function composeShellModel(context: ShellRuntimeContext): ResolvedShellModel {
  const activeModules = resolveActiveModules(context);

  const primaryNavCandidates = filterVisibleNavItems(
    filterByModules(
      navRegistry.filter((item) => item.slot === "primaryNavSlot"),
      activeModules,
      (moduleId) => moduleRegistry.find((module) => module.id === moduleId)?.navItemIds ?? []
    ),
    context
  );
  const secondaryNavCandidates = filterVisibleNavItems(
    navRegistry.filter((item) => item.slot === "secondaryNavSlot"),
    context
  );

  const quickActionCandidates = filterVisibleActions(
    filterByModules(
      sortByPriority(CLIENT_ACTIONS.filter((action) => action.slot === "quickActionSlot")),
      activeModules,
      (moduleId) => moduleRegistry.find((module) => module.id === moduleId)?.actionIds ?? []
    ),
    context
  );
  const contextActionCandidates = filterVisibleActions(
    sortByPriority(CLIENT_ACTIONS.filter((action) => action.slot === "contextActionSlot")),
    context
  );
  const utilityCandidates = filterVisibleActions(
    sortByPriority(CLIENT_ACTIONS.filter((action) => action.slot === "utilitySlot")),
    context
  );

  const contextualWidgetCandidates = filterVisibleWidgets(
    filterByModules(
      sortByPriority(CLIENT_WIDGETS.filter((widget) => widget.slot === "contextualPanelSlot")),
      activeModules,
      (moduleId) => moduleRegistry.find((module) => module.id === moduleId)?.widgetIds ?? []
    ),
    context
  );
  const quickFilterWidgetCandidates = filterVisibleWidgets(
    sortByPriority(CLIENT_WIDGETS.filter((widget) => widget.slot === "quickFiltersSlot")),
    context
  );
  const pluginWidgetCandidates = filterVisibleWidgets(
    sortByPriority(CLIENT_WIDGETS.filter((widget) => widget.slot === "pluginTraySlot")),
    context
  );

  return {
    brandSlot: validateBrandSlot({
      slotId: "brandSlot",
      ...CLIENT_MANIFEST.slots.brandSlot
    }),
    workspaceSlot: validateWorkspaceSlot({
      slotId: "workspaceSlot",
      ...CLIENT_MANIFEST.slots.workspaceSlot
    }),
    primaryNavSlot: navSlotPayload("primaryNavSlot", primaryNavCandidates),
    secondaryNavSlot: navSlotPayload("secondaryNavSlot", secondaryNavCandidates),
    quickActionSlot: actionSlotPayload("quickActionSlot", quickActionCandidates),
    contextActionSlot: actionSlotPayload("contextActionSlot", contextActionCandidates),
    utilitySlot: actionSlotPayload("utilitySlot", utilityCandidates),
    footerSlot: validateFooterSlot({
      slotId: "footerSlot",
      ...CLIENT_MANIFEST.slots.footerSlot
    }),
    contextualPanelSlot: widgetSlotPayload("contextualPanelSlot", contextualWidgetCandidates),
    quickFiltersSlot: widgetSlotPayload("quickFiltersSlot", quickFilterWidgetCandidates),
    pluginTraySlot: widgetSlotPayload("pluginTraySlot", pluginWidgetCandidates)
  };
}
