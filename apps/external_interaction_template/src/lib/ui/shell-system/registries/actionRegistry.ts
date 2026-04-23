import { CLIENT_ACTIONS } from "@/lib/ui/shell-system/client/client.actions";
import type { ActionDescriptor } from "@/lib/ui/shell-system/types";
import { validateActionItems } from "@/lib/ui/shell-system/validators";

const ordered = [...CLIENT_ACTIONS].sort((left, right) => left.priority - right.priority);

export const actionRegistry = validateActionItems(ordered);

export function getActionsBySlot(slot: ActionDescriptor["slot"]): ActionDescriptor[] {
  return actionRegistry.filter((action) => action.slot === slot);
}

export function getActionById(id: string): ActionDescriptor | undefined {
  return actionRegistry.find((action) => action.id === id);
}

