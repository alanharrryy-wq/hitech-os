import { z } from "zod";

import type { UiArea } from "@/lib/ui/runtime";
import type { UiThemeId } from "@/lib/ui/theme-system";

export const SHELL_SLOT_IDS = [
  "brandSlot",
  "workspaceSlot",
  "primaryNavSlot",
  "secondaryNavSlot",
  "quickActionSlot",
  "contextActionSlot",
  "utilitySlot",
  "footerSlot",
  "contextualPanelSlot",
  "quickFiltersSlot",
  "pluginTraySlot"
] as const;

export type ShellSlotId = (typeof SHELL_SLOT_IDS)[number];
export type ShellBreakpoint = "desktop" | "tablet" | "mobile";
export type SlotEmptyBehavior = "collapse" | "placeholder" | "hidden";
export type SlotVisibilityMode = "show" | "hide" | "drawer";
export type SlotCollapsedLabelPolicy = "tooltip" | "always" | "hidden";
export type SlotMobilePolicy = "show" | "hide" | "drawer";

export const ICON_FAMILIES = ["set_01_nebula_midnight", "set_02_pearl_mist", "set_03_nova_rose", "system"] as const;
export type IconFamily = (typeof ICON_FAMILIES)[number];

export interface IconDescriptor {
  family: IconFamily;
  name: string;
  alt?: string;
}

export interface SlotBadgeDescriptor {
  text?: string;
  tone?: "default" | "accent" | "success" | "warning" | "danger";
  resolverId?: string;
}

export interface VisibilityPolicy {
  whenAreas?: string[];
  hideAreas?: string[];
  requiredPermissions?: string[];
  minBreakpoint?: ShellBreakpoint;
  maxBreakpoint?: ShellBreakpoint;
}

export interface SlotVisibilityPolicy {
  desktop: SlotVisibilityMode;
  tablet: SlotVisibilityMode;
  mobile: SlotVisibilityMode;
}

export interface BreakpointBehavior {
  desktop: "expanded" | "compact";
  tablet: "expanded" | "compact";
  mobile: "stack" | "drawer" | "hidden";
}

export interface SlotPayloadBase {
  slotId: ShellSlotId;
  visibility: VisibilityPolicy;
  slotVisibility: SlotVisibilityPolicy;
  emptyBehavior: SlotEmptyBehavior;
  breakpoints: BreakpointBehavior;
}

export interface BrandSlotPayload extends SlotPayloadBase {
  slotId: "brandSlot";
  label: string;
  logo?: IconDescriptor;
  href?: string;
  subtitle?: string;
}

export interface WorkspaceSlotPayload extends SlotPayloadBase {
  slotId: "workspaceSlot";
  title: string;
  description?: string;
  icon?: IconDescriptor;
  badge?: SlotBadgeDescriptor;
}

export type NavSlotTarget = "primaryNavSlot" | "secondaryNavSlot" | "utilitySlot";

export interface NavItemDescriptor {
  id: string;
  labelKey: string;
  iconFamily: IconFamily;
  iconName: string;
  route: string;
  group: "core" | "ops" | "support" | "system";
  priority: number;
  visibility: VisibilityPolicy;
  permissions: string[];
  slot: NavSlotTarget;
  badge?: SlotBadgeDescriptor;
  children?: NavItemDescriptor[];
  tooltip?: string;
  mobilePolicy: SlotMobilePolicy;
  collapsedLabelPolicy: SlotCollapsedLabelPolicy;
}

export interface NavSlotPayload extends SlotPayloadBase {
  slotId: NavSlotTarget;
  items: NavItemDescriptor[];
}

export interface ActionDescriptor {
  id: string;
  labelKey: string;
  iconFamily?: IconFamily;
  iconName?: string;
  slot: "quickActionSlot" | "contextActionSlot" | "utilitySlot";
  priority: number;
  variant: "primary" | "secondary" | "ghost" | "danger";
  href?: string;
  visibility: VisibilityPolicy;
  permissions: string[];
  badge?: SlotBadgeDescriptor;
  mobilePolicy: SlotMobilePolicy;
}

export interface ActionSlotPayload extends SlotPayloadBase {
  slotId: "quickActionSlot" | "contextActionSlot" | "utilitySlot";
  items: ActionDescriptor[];
}

export interface FooterSlotPayload extends SlotPayloadBase {
  slotId: "footerSlot";
  text: string;
  links?: Array<{ label: string; href: string }>;
}

export interface WidgetDescriptor {
  id: string;
  titleKey: string;
  summaryKey?: string;
  slot: "contextualPanelSlot" | "quickFiltersSlot" | "pluginTraySlot";
  priority: number;
  icon?: IconDescriptor;
  badge?: SlotBadgeDescriptor;
  visibility: VisibilityPolicy;
  permissions: string[];
  componentId: string;
  mobilePolicy: SlotMobilePolicy;
}

export interface WidgetSlotPayload extends SlotPayloadBase {
  slotId: "contextualPanelSlot" | "quickFiltersSlot" | "pluginTraySlot";
  widgets: WidgetDescriptor[];
}

export interface ModuleDescriptor {
  id: string;
  labelKey: string;
  routePrefix: string;
  defaultArea: UiArea;
  navItemIds: string[];
  actionIds: string[];
  widgetIds: string[];
  visibility: VisibilityPolicy;
  permissions: string[];
}

export interface ClientThemeBinding {
  id: UiThemeId;
  iconFamily: Exclude<IconFamily, "system">;
}

export interface ClientThemeManifest {
  defaultTheme: UiThemeId;
  bindings: ClientThemeBinding[];
}

export interface ClientPermissionsManifest {
  defaultPermissions: string[];
}

export interface ClientManifest {
  id: string;
  label: string;
  workspaceLabel: string;
  workspaceDescription: string;
  slots: {
    brandSlot: Omit<BrandSlotPayload, "slotId">;
    workspaceSlot: Omit<WorkspaceSlotPayload, "slotId">;
    footerSlot: Omit<FooterSlotPayload, "slotId">;
  };
}

export interface ShellRuntimeContext {
  area: UiArea;
  currentPath: string;
  themeId: UiThemeId;
  locale: string;
  breakpoint: ShellBreakpoint;
  collapsedSidebar: boolean;
  permissions: Set<string>;
}

export interface ResolvedShellSlotState {
  visible: boolean;
  mode: SlotVisibilityMode;
  reason?: string;
}

export interface ResolvedShellModel {
  brandSlot?: BrandSlotPayload;
  workspaceSlot?: WorkspaceSlotPayload;
  primaryNavSlot?: NavSlotPayload;
  secondaryNavSlot?: NavSlotPayload;
  quickActionSlot?: ActionSlotPayload;
  contextActionSlot?: ActionSlotPayload;
  utilitySlot?: ActionSlotPayload;
  footerSlot?: FooterSlotPayload;
  contextualPanelSlot?: WidgetSlotPayload;
  quickFiltersSlot?: WidgetSlotPayload;
  pluginTraySlot?: WidgetSlotPayload;
}

export const iconDescriptorSchema = z.object({
  family: z.enum(ICON_FAMILIES),
  name: z.string().min(1),
  alt: z.string().optional()
});

export const visibilityPolicySchema = z.object({
  whenAreas: z.array(z.string()).optional(),
  hideAreas: z.array(z.string()).optional(),
  requiredPermissions: z.array(z.string()).optional(),
  minBreakpoint: z.enum(["desktop", "tablet", "mobile"]).optional(),
  maxBreakpoint: z.enum(["desktop", "tablet", "mobile"]).optional()
});

export const slotVisibilitySchema = z.object({
  desktop: z.enum(["show", "hide", "drawer"]),
  tablet: z.enum(["show", "hide", "drawer"]),
  mobile: z.enum(["show", "hide", "drawer"])
});

export const breakpointBehaviorSchema = z.object({
  desktop: z.enum(["expanded", "compact"]),
  tablet: z.enum(["expanded", "compact"]),
  mobile: z.enum(["stack", "drawer", "hidden"])
});

export const slotPayloadBaseSchema = z.object({
  visibility: visibilityPolicySchema,
  slotVisibility: slotVisibilitySchema,
  emptyBehavior: z.enum(["collapse", "placeholder", "hidden"]),
  breakpoints: breakpointBehaviorSchema
});
