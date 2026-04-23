import type { ActionDescriptor, NavItemDescriptor, ShellRuntimeContext, VisibilityPolicy, WidgetDescriptor } from "@/lib/ui/shell-system/types";

const BREAKPOINT_ORDER = {
  mobile: 0,
  tablet: 1,
  desktop: 2
} as const;

function hasRequiredPermissions(requiredPermissions: readonly string[] | undefined, context: ShellRuntimeContext): boolean {
  if (!requiredPermissions || requiredPermissions.length === 0) return true;
  return requiredPermissions.every((permission) => context.permissions.has(permission));
}

function inBreakpointRange(policy: VisibilityPolicy, context: ShellRuntimeContext): boolean {
  const current = BREAKPOINT_ORDER[context.breakpoint];
  const min = BREAKPOINT_ORDER[policy.minBreakpoint ?? "mobile"];
  const max = BREAKPOINT_ORDER[policy.maxBreakpoint ?? "desktop"];
  return current >= min && current <= max;
}

export function isVisibleByPolicy(policy: VisibilityPolicy, context: ShellRuntimeContext): boolean {
  if (!inBreakpointRange(policy, context)) return false;
  if (policy.whenAreas && policy.whenAreas.length > 0 && !policy.whenAreas.includes(context.area)) return false;
  if (policy.hideAreas?.includes(context.area)) return false;
  if (!hasRequiredPermissions(policy.requiredPermissions, context)) return false;
  return true;
}

export function filterVisibleNavItems(items: NavItemDescriptor[], context: ShellRuntimeContext): NavItemDescriptor[] {
  return items
    .filter((item) => isVisibleByPolicy(item.visibility, context))
    .filter((item) => item.permissions.every((permission) => context.permissions.has(permission)))
    .map((item) => ({
      ...item,
      children: item.children ? filterVisibleNavItems(item.children, context) : undefined
    }));
}

export function filterVisibleActions(items: ActionDescriptor[], context: ShellRuntimeContext): ActionDescriptor[] {
  return items
    .filter((item) => isVisibleByPolicy(item.visibility, context))
    .filter((item) => item.permissions.every((permission) => context.permissions.has(permission)));
}

export function filterVisibleWidgets(items: WidgetDescriptor[], context: ShellRuntimeContext): WidgetDescriptor[] {
  return items
    .filter((item) => isVisibleByPolicy(item.visibility, context))
    .filter((item) => item.permissions.every((permission) => context.permissions.has(permission)));
}

