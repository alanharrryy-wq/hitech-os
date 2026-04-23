export { CLIENT_ACTIONS } from "@/lib/ui/shell-system/client/client.actions";
export { CLIENT_MANIFEST } from "@/lib/ui/shell-system/client/client.manifest";
export { CLIENT_NAV_ITEMS } from "@/lib/ui/shell-system/client/client.navigation";
export { CLIENT_DEFAULT_PERMISSIONS, CLIENT_PERMISSION_KEYS, type ClientPermissionKey } from "@/lib/ui/shell-system/client/client.permissions";
export { CLIENT_THEME_MANIFEST, resolveIconFamilyByTheme } from "@/lib/ui/shell-system/client/client.theme";
export { CLIENT_WIDGETS } from "@/lib/ui/shell-system/client/client.widgets";
export { actionRegistry, getActionById, getActionsBySlot } from "@/lib/ui/shell-system/registries/actionRegistry";
export { moduleRegistry } from "@/lib/ui/shell-system/registries/moduleRegistry";
export { getNavItemById, getNavItemsBySlot, navRegistry } from "@/lib/ui/shell-system/registries/navRegistry";
export { getWidgetById, getWidgetsBySlot, widgetRegistry } from "@/lib/ui/shell-system/registries/widgetRegistry";
export { createShellPermissionsSet, composeShellModel } from "@/lib/ui/shell-system/composeShellModel";
export { resolveBadge, type BadgeResolverContext } from "@/lib/ui/shell-system/badgeResolvers";
export { filterVisibleActions, filterVisibleNavItems, filterVisibleWidgets, isVisibleByPolicy } from "@/lib/ui/shell-system/visibility";
export type {
  ActionDescriptor,
  ActionSlotPayload,
  BrandSlotPayload,
  BreakpointBehavior,
  ClientManifest,
  ClientThemeBinding,
  ClientThemeManifest,
  FooterSlotPayload,
  IconDescriptor,
  IconFamily,
  ModuleDescriptor,
  NavItemDescriptor,
  NavSlotPayload,
  ResolvedShellModel,
  ResolvedShellSlotState,
  ShellBreakpoint,
  ShellRuntimeContext,
  ShellSlotId,
  SlotBadgeDescriptor,
  SlotCollapsedLabelPolicy,
  SlotEmptyBehavior,
  SlotMobilePolicy,
  SlotPayloadBase,
  SlotVisibilityMode,
  SlotVisibilityPolicy,
  VisibilityPolicy,
  WidgetDescriptor,
  WidgetSlotPayload,
  WorkspaceSlotPayload
} from "@/lib/ui/shell-system/types";
