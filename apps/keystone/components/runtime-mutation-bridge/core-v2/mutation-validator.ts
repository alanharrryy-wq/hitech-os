import {
  getLayoutNode,
  getPrefabCompatibilityIssues,
  getSlot,
  getWidget,
  type SceneDocument,
} from "./scene-domain";
import { AUTHORING_WORKBENCH_V2_MUTATION_SOURCE, type RuntimeMutationCommand } from "./mutation-contract";
import type { ValidationIssue, ValidationResult } from "./mutation-result";

const SAFE_MODE_ALLOWED_COMMANDS = new Set<RuntimeMutationCommand["type"]>([
  "scene.look.update",
  "layout.node.move",
  "layout.node.resize",
  "widget.update-props",
  "widget.update-style",
  "selection.reset",
  "draft.commit",
  "draft.discard",
]);

function push(issues: ValidationIssue[], code: ValidationIssue["code"], message: string): void {
  issues.push({ code, message });
}

export function validateRuntimeMutationCommand(command: RuntimeMutationCommand, baseline: SceneDocument, draft: SceneDocument): ValidationResult {
  const issues: ValidationIssue[] = [];

  if (command.source !== AUTHORING_WORKBENCH_V2_MUTATION_SOURCE) {
    push(issues, "invalid-source", "Mutation source is not allowed to write through core-v2.");
  }

  if (command.mode === "safe" && !SAFE_MODE_ALLOWED_COMMANDS.has(command.type)) {
    push(issues, "safe-mode-rejected", `Safe Mode rejected ${command.type}.`);
  }

  if (command.scope === "accepted-state-transition" && command.type !== "draft.commit") {
    push(issues, "invalid-scope", "Accepted-state-transition scope is reserved for draft.commit.");
  }
  if (command.scope === "full-draft-discard" && command.type !== "draft.discard") {
    push(issues, "invalid-scope", "Full-draft-discard scope is reserved for draft.discard.");
  }
  if (command.scope === "local-reset" && command.type !== "selection.reset") {
    push(issues, "invalid-scope", "Local-reset scope is reserved for selection.reset.");
  }

  if ((command.type === "draft.commit" || command.type === "draft.discard") && command.target.kind !== "draft") {
    push(issues, "draft-target-required", `${command.type} must target the draft.`);
  }

  if (command.target.kind !== "draft" && command.target.sceneId !== draft.scene.id) {
    push(issues, "invalid-target", "Mutation target scene does not match the current draft scene.");
  }

  if (command.type === "draft.commit" || command.type === "draft.discard") {
    return { accepted: issues.length === 0, issues };
  }

  if (command.target.kind === "scene") {
    if (command.target.id !== draft.scene.id) {
      push(issues, "invalid-target", "Scene target does not match the draft scene.");
    }
  }

  if (command.target.kind === "layout-node") {
    const node = getLayoutNode(draft, command.target.id);
    if (!node) {
      push(issues, "missing-entity", "Layout node target does not exist in draft state.");
    } else if (node.locked || node.kind === "root") {
      push(issues, "locked-target", "Layout target is locked or protected.");
    }
  }

  if (command.target.kind === "slot") {
    const slot = getSlot(draft, command.target.id);
    if (!slot) {
      push(issues, "missing-entity", "Slot target does not exist in draft state.");
    } else if (slot.locked) {
      push(issues, "locked-target", "Slot target is locked.");
    }
  }

  if (command.target.kind === "widget") {
    const widget = getWidget(draft, command.target.id);
    if (!widget) {
      push(issues, "missing-entity", "Widget target does not exist in draft state.");
    } else if (widget.locked) {
      push(issues, "locked-target", "Widget target is locked.");
    }
  }

  switch (command.type) {
    case "scene.look.update": {
      if (command.target.kind !== "scene") {
        push(issues, "invalid-target", "Scene look updates must target the scene.");
      }
      break;
    }
    case "layout.node.move": {
      if (command.target.kind !== "layout-node") {
        push(issues, "invalid-target", "Layout move must target a layout node.");
      }
      if (!Number.isFinite(command.payload.deltaX) || !Number.isFinite(command.payload.deltaY)) {
        push(issues, "out-of-range", "Layout move deltas must be finite numbers.");
      }
      break;
    }
    case "layout.node.resize": {
      if (command.target.kind !== "layout-node") {
        push(issues, "invalid-target", "Layout resize must target a layout node.");
      }
      if (!Number.isFinite(command.payload.widthDelta) || !Number.isFinite(command.payload.heightDelta)) {
        push(issues, "out-of-range", "Layout resize deltas must be finite numbers.");
      }
      break;
    }
    case "layout.node.reorder": {
      if (command.target.kind !== "layout-node") {
        push(issues, "invalid-target", "Layout reorder must target a layout node.");
        break;
      }
      const node = getLayoutNode(draft, command.target.id);
      if (!node || !node.parentId) {
        push(issues, "invalid-target", "Layout reorder requires a non-root layout node.");
        break;
      }
      const parent = getLayoutNode(draft, node.parentId);
      if (!parent) {
        push(issues, "missing-entity", "Parent layout node was not found for reorder.");
        break;
      }
      if (command.payload.toIndex < 0 || command.payload.toIndex >= parent.childIds.length) {
        push(issues, "out-of-range", "Layout reorder target index is out of range.");
      }
      break;
    }
    case "widget.insert-from-prefab": {
      if (command.target.kind !== "slot") {
        push(issues, "invalid-target", "Widget insertion must target a slot.");
        break;
      }
      if (command.payload.slotId !== command.target.id) {
        push(issues, "invalid-target", "Widget insertion payload slotId must match the target slot.");
      }
      const slot = getSlot(draft, command.payload.slotId);
      if (!slot) {
        push(issues, "missing-entity", "Insert target slot does not exist.");
        break;
      }
      const compatibilityIssues = getPrefabCompatibilityIssues(slot, command.payload.prefab);
      if (compatibilityIssues.includes("capacity")) {
        push(issues, "slot-capacity-exceeded", "Slot capacity would be exceeded by prefab insertion.");
      }
      if (compatibilityIssues.includes("slot-kind")) {
        push(issues, "slot-incompatible", "Prefab slot-kind policy rejects the target slot.");
      }
      if (compatibilityIssues.includes("widget-type")) {
        push(issues, "slot-incompatible", "Slot widget-type policy rejects the prefab.");
      }
      if (compatibilityIssues.includes("capability")) {
        push(issues, "slot-incompatible", "Slot capability policy rejects the prefab.");
      }
      break;
    }
    case "widget.update-props": {
      if (command.target.kind !== "widget") {
        push(issues, "invalid-target", "Widget prop updates must target a widget.");
      }
      break;
    }
    case "widget.update-style": {
      if (command.target.kind !== "widget") {
        push(issues, "invalid-target", "Widget style updates must target a widget.");
      }
      break;
    }
    case "widget.remove": {
      if (command.target.kind !== "widget") {
        push(issues, "invalid-target", "Widget removal must target a widget.");
      }
      if (command.payload.widgetId !== command.target.id) {
        push(issues, "invalid-target", "Widget removal payload widgetId must match the target widget.");
      }
      if (!getWidget(draft, command.payload.widgetId)) {
        push(issues, "missing-entity", "Widget removal target does not exist.");
      }
      break;
    }
    case "selection.reset": {
      if (command.target.kind === "draft") {
        push(issues, "invalid-target", "Selection reset must target scene, layout node, slot, or widget.");
      }
      if (command.payload.baselineSceneId !== baseline.scene.id) {
        push(issues, "baseline-missing", "Selection reset requires the matching baseline scene.");
      }
      break;
    }
    default: {
      push(issues, "invalid-command", `Unknown runtime mutation command ${(command as { readonly type: string }).type}.`);
      break;
    }
  }

  return { accepted: issues.length === 0, issues };
}
