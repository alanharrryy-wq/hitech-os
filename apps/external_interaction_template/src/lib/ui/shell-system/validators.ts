import { z } from "zod";

import {
  iconDescriptorSchema,
  slotPayloadBaseSchema,
  visibilityPolicySchema,
  type ActionDescriptor,
  type ActionSlotPayload,
  type BrandSlotPayload,
  type FooterSlotPayload,
  type ModuleDescriptor,
  type NavItemDescriptor,
  type NavSlotPayload,
  type ResolvedShellSlotState,
  type ShellBreakpoint,
  type ShellRuntimeContext,
  type SlotVisibilityMode,
  type WidgetDescriptor,
  type WidgetSlotPayload,
  type WorkspaceSlotPayload
} from "@/lib/ui/shell-system/types";

const badgeSchema = z.object({
  text: z.string().optional(),
  tone: z.enum(["default", "accent", "success", "warning", "danger"]).optional(),
  resolverId: z.string().optional()
});

const navItemSchema: z.ZodType<NavItemDescriptor> = z.lazy(() =>
  z.object({
    id: z.string().min(1),
    labelKey: z.string().min(1),
    iconFamily: z.enum(["set_01_nebula_midnight", "set_02_pearl_mist", "set_03_nova_rose", "system"]),
    iconName: z.string().min(1),
    route: z.string().startsWith("/"),
    group: z.enum(["core", "ops", "support", "system"]),
    priority: z.number().int(),
    visibility: visibilityPolicySchema,
    permissions: z.array(z.string()),
    slot: z.enum(["primaryNavSlot", "secondaryNavSlot", "utilitySlot"]),
    badge: badgeSchema.optional(),
    children: z.array(navItemSchema).optional(),
    tooltip: z.string().optional(),
    mobilePolicy: z.enum(["show", "hide", "drawer"]),
    collapsedLabelPolicy: z.enum(["tooltip", "always", "hidden"])
  })
);

const actionDescriptorSchema: z.ZodType<ActionDescriptor> = z.object({
  id: z.string().min(1),
  labelKey: z.string().min(1),
  iconFamily: z.enum(["set_01_nebula_midnight", "set_02_pearl_mist", "set_03_nova_rose", "system"]).optional(),
  iconName: z.string().optional(),
  slot: z.enum(["quickActionSlot", "contextActionSlot", "utilitySlot"]),
  priority: z.number().int(),
  variant: z.enum(["primary", "secondary", "ghost", "danger"]),
  href: z.string().startsWith("/").optional(),
  visibility: visibilityPolicySchema,
  permissions: z.array(z.string()),
  badge: badgeSchema.optional(),
  mobilePolicy: z.enum(["show", "hide", "drawer"])
});

const widgetDescriptorSchema: z.ZodType<WidgetDescriptor> = z.object({
  id: z.string().min(1),
  titleKey: z.string().min(1),
  summaryKey: z.string().optional(),
  slot: z.enum(["contextualPanelSlot", "quickFiltersSlot", "pluginTraySlot"]),
  priority: z.number().int(),
  icon: iconDescriptorSchema.optional(),
  badge: badgeSchema.optional(),
  visibility: visibilityPolicySchema,
  permissions: z.array(z.string()),
  componentId: z.string().min(1),
  mobilePolicy: z.enum(["show", "hide", "drawer"])
});

const brandSlotSchema: z.ZodType<BrandSlotPayload> = z.object({
  slotId: z.literal("brandSlot"),
  label: z.string().min(1),
  logo: iconDescriptorSchema.optional(),
  href: z.string().startsWith("/").optional(),
  subtitle: z.string().optional(),
  ...slotPayloadBaseSchema.shape
});

const workspaceSlotSchema: z.ZodType<WorkspaceSlotPayload> = z.object({
  slotId: z.literal("workspaceSlot"),
  title: z.string().min(1),
  description: z.string().optional(),
  icon: iconDescriptorSchema.optional(),
  badge: badgeSchema.optional(),
  ...slotPayloadBaseSchema.shape
});

const footerSlotSchema: z.ZodType<FooterSlotPayload> = z.object({
  slotId: z.literal("footerSlot"),
  text: z.string().min(1),
  links: z.array(z.object({ label: z.string().min(1), href: z.string().startsWith("/") })).optional(),
  ...slotPayloadBaseSchema.shape
});

const navSlotSchema: z.ZodType<NavSlotPayload> = z.object({
  slotId: z.enum(["primaryNavSlot", "secondaryNavSlot", "utilitySlot"]),
  items: z.array(navItemSchema),
  ...slotPayloadBaseSchema.shape
});

const actionSlotSchema: z.ZodType<ActionSlotPayload> = z.object({
  slotId: z.enum(["quickActionSlot", "contextActionSlot", "utilitySlot"]),
  items: z.array(actionDescriptorSchema),
  ...slotPayloadBaseSchema.shape
});

const widgetSlotSchema: z.ZodType<WidgetSlotPayload> = z.object({
  slotId: z.enum(["contextualPanelSlot", "quickFiltersSlot", "pluginTraySlot"]),
  widgets: z.array(widgetDescriptorSchema),
  ...slotPayloadBaseSchema.shape
});

const moduleSchema: z.ZodType<ModuleDescriptor> = z.object({
  id: z.string().min(1),
  labelKey: z.string().min(1),
  routePrefix: z.string().startsWith("/"),
  defaultArea: z.enum(["launcher", "inbox", "flow", "record", "sync", "system", "generic"]),
  navItemIds: z.array(z.string().min(1)),
  actionIds: z.array(z.string().min(1)),
  widgetIds: z.array(z.string().min(1)),
  visibility: visibilityPolicySchema,
  permissions: z.array(z.string())
});

export function validateBrandSlot(payload: BrandSlotPayload): BrandSlotPayload {
  return brandSlotSchema.parse(payload);
}

export function validateWorkspaceSlot(payload: WorkspaceSlotPayload): WorkspaceSlotPayload {
  return workspaceSlotSchema.parse(payload);
}

export function validateFooterSlot(payload: FooterSlotPayload): FooterSlotPayload {
  return footerSlotSchema.parse(payload);
}

export function validateNavItems(items: NavItemDescriptor[]): NavItemDescriptor[] {
  return z.array(navItemSchema).parse(items);
}

export function validateActionItems(items: ActionDescriptor[]): ActionDescriptor[] {
  return z.array(actionDescriptorSchema).parse(items);
}

export function validateWidgetItems(items: WidgetDescriptor[]): WidgetDescriptor[] {
  return z.array(widgetDescriptorSchema).parse(items);
}

export function validateNavSlot(payload: NavSlotPayload): NavSlotPayload {
  return navSlotSchema.parse(payload);
}

export function validateActionSlot(payload: ActionSlotPayload): ActionSlotPayload {
  return actionSlotSchema.parse(payload);
}

export function validateWidgetSlot(payload: WidgetSlotPayload): WidgetSlotPayload {
  return widgetSlotSchema.parse(payload);
}

export function validateModules(items: ModuleDescriptor[]): ModuleDescriptor[] {
  return z.array(moduleSchema).parse(items);
}

const BREAKPOINT_ORDER: Record<ShellBreakpoint, number> = {
  mobile: 0,
  tablet: 1,
  desktop: 2
};

function hasRequiredPermissions(requiredPermissions: readonly string[] | undefined, context: ShellRuntimeContext): boolean {
  if (!requiredPermissions || requiredPermissions.length === 0) return true;
  return requiredPermissions.every((permission) => context.permissions.has(permission));
}

function isBetweenBreakpoint(min: ShellBreakpoint | undefined, max: ShellBreakpoint | undefined, current: ShellBreakpoint): boolean {
  const currentOrder = BREAKPOINT_ORDER[current];
  const minOrder = min ? BREAKPOINT_ORDER[min] : BREAKPOINT_ORDER.mobile;
  const maxOrder = max ? BREAKPOINT_ORDER[max] : BREAKPOINT_ORDER.desktop;
  return currentOrder >= minOrder && currentOrder <= maxOrder;
}

export function resolveSlotState(visibility: z.infer<typeof visibilityPolicySchema>, context: ShellRuntimeContext): ResolvedShellSlotState {
  if (!isBetweenBreakpoint(visibility.minBreakpoint, visibility.maxBreakpoint, context.breakpoint)) {
    return { visible: false, mode: "hide", reason: "breakpoint-out-of-range" };
  }
  if (visibility.whenAreas && visibility.whenAreas.length > 0 && !visibility.whenAreas.includes(context.area)) {
    return { visible: false, mode: "hide", reason: "area-not-allowed" };
  }
  if (visibility.hideAreas?.includes(context.area)) {
    return { visible: false, mode: "hide", reason: "area-hidden" };
  }
  if (!hasRequiredPermissions(visibility.requiredPermissions, context)) {
    return { visible: false, mode: "hide", reason: "permission-denied" };
  }
  return { visible: true, mode: "show" };
}

export function resolveVisibilityMode(mode: { desktop: SlotVisibilityMode; tablet: SlotVisibilityMode; mobile: SlotVisibilityMode }, context: ShellRuntimeContext): SlotVisibilityMode {
  if (context.breakpoint === "mobile") return mode.mobile;
  if (context.breakpoint === "tablet") return mode.tablet;
  return mode.desktop;
}
