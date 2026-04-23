import { CLIENT_WIDGETS } from "@/lib/ui/shell-system/client/client.widgets";
import type { WidgetDescriptor } from "@/lib/ui/shell-system/types";
import { validateWidgetItems } from "@/lib/ui/shell-system/validators";

const ordered = [...CLIENT_WIDGETS].sort((left, right) => left.priority - right.priority);

export const widgetRegistry = validateWidgetItems(ordered);

export function getWidgetsBySlot(slot: WidgetDescriptor["slot"]): WidgetDescriptor[] {
  return widgetRegistry.filter((widget) => widget.slot === slot);
}

export function getWidgetById(id: string): WidgetDescriptor | undefined {
  return widgetRegistry.find((widget) => widget.id === id);
}

