import { CLIENT_NAV_ITEMS } from "@/lib/ui/shell-system/client/client.navigation";
import type { NavItemDescriptor } from "@/lib/ui/shell-system/types";
import { validateNavItems } from "@/lib/ui/shell-system/validators";

const ordered = [...CLIENT_NAV_ITEMS].sort((left, right) => left.priority - right.priority);

export const navRegistry = validateNavItems(ordered);

export function getNavItemsBySlot(slot: NavItemDescriptor["slot"]): NavItemDescriptor[] {
  return navRegistry.filter((item) => item.slot === slot);
}

export function getNavItemById(id: string): NavItemDescriptor | undefined {
  return navRegistry.find((item) => item.id === id);
}

