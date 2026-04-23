import {
  type ActionDefinition,
  type ActorContext,
  type ExternalRecord,
  type RecordState
} from "@/lib/core/types";

const terminalStates = new Set<RecordState>(["synced", "failed"]);

export function canTransition(current: RecordState, target: RecordState): boolean {
  if (current === target) return true;
  if (terminalStates.has(current) && target === "dispatched") {
    return true;
  }

  const map: Record<RecordState, RecordState[]> = {
    draft: ["submitted", "failed"],
    submitted: ["in_review", "awaiting_update", "approved", "rejected", "failed"],
    in_review: ["awaiting_update", "approved", "rejected", "dispatched", "failed"],
    awaiting_update: ["submitted", "in_review", "failed"],
    approved: ["dispatched", "synced", "failed"],
    rejected: ["awaiting_update", "failed"],
    dispatched: ["synced", "failed"],
    synced: ["failed"],
    failed: ["draft", "submitted", "in_review", "awaiting_update"]
  };

  return map[current].includes(target);
}

export function isActionAvailable(
  recordState: RecordState,
  action: ActionDefinition,
  actor: ActorContext
): boolean {
  if (!action.allowedStates.includes(recordState)) return false;
  if (action.allowedRoles && action.allowedRoles.length > 0 && !action.allowedRoles.includes(actor.role)) {
    return false;
  }
  return true;
}

export function ensureActionAvailable(record: ExternalRecord, action: ActionDefinition, actor: ActorContext) {
  if (!isActionAvailable(record.state, action, actor)) {
    throw new Error(`Action '${action.id}' is not available for state '${record.state}' and role '${actor.role}'`);
  }
}
