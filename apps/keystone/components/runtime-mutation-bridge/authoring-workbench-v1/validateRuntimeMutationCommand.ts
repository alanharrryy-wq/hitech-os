import type { RuntimeMutationCommand, RuntimeMutationValidationError, RuntimeMutationValidationResult, SceneDocument } from "./contract";

const SAFE_MODE_COMMANDS = new Set<string>([
  "scene.look.update",
  "layout.node.move",
  "layout.node.resize",
  "layout.node.reorder",
  "widget.insert-from-prefab",
  "widget.update-props",
  "widget.update-style",
  "widget.remove",
  "selection.reset",
  "draft.commit",
  "draft.discard",
]);

function push(errors: RuntimeMutationValidationError[], code: RuntimeMutationValidationError["code"], message: string): void {
  errors.push({ code, message });
}

export function validateRuntimeMutationCommand(command: RuntimeMutationCommand, baseline: SceneDocument, draft: SceneDocument): RuntimeMutationValidationResult {
  const errors: RuntimeMutationValidationError[] = [];
  if (command.source !== "live-scene-composer.authoring-workbench-v1") {
    push(errors, "invalid-source", "Mutation source is not allowed to write through the wave 1 bridge.");
  }
  if (command.mode === "safe" && !SAFE_MODE_COMMANDS.has(command.type)) {
    push(errors, "safe-mode-rejected", `Safe Mode rejected ${command.type}.`);
  }
  if (command.scope === "accepted-state-transition" && command.type !== "draft.commit") {
    push(errors, "invalid-scope", "Accepted-state transitions are reserved for explicit draft commits.");
  }
  if (command.scope === "full-draft-discard" && command.type !== "draft.discard") {
    push(errors, "invalid-scope", "Full draft discard is reserved for draft.discard.");
  }
  if (command.type === "draft.commit" || command.type === "draft.discard") {
    return { accepted: errors.length === 0, errors };
  }
  if (command.target.kind === "scene") {
    if (command.target.id !== draft.scene.id) {
      push(errors, "invalid-target", "Scene target does not match the draft scene.");
    }
  } else if (command.target.kind === "layout-node") {
    const node = draft.layoutNodes[command.target.id];
    if (!node) {
      push(errors, "missing-entity", "Layout node target does not exist in draft state.");
    } else if (node.locked || node.kind === "root") {
      push(errors, "locked-target", "Layout target is locked or protected.");
    }
  } else if (command.target.kind === "slot") {
    const slot = draft.slots[command.target.id];
    if (!slot) {
      push(errors, "missing-entity", "Slot target does not exist in draft state.");
    } else if (slot.locked) {
      push(errors, "locked-target", "Slot target is locked.");
    }
  } else if (command.target.kind === "widget") {
    const widget = draft.widgets[command.target.id];
    if (!widget) {
      push(errors, "missing-entity", "Widget target does not exist in draft state.");
    } else if (widget.locked) {
      push(errors, "locked-target", "Widget target is locked.");
    }
  }

  switch (command.type) {
    case "scene.look.update": {
      if (command.target.kind !== "scene") {
        push(errors, "invalid-target", "Scene look updates must target the scene.");
      }
      break;
    }
    case "layout.node.move": {
      if (command.target.kind !== "layout-node") {
        push(errors, "invalid-target", "Layout move must target a layout node.");
      }
      if (!Number.isFinite(command.payload.deltaX) || !Number.isFinite(command.payload.deltaY)) {
        push(errors, "out-of-range", "Layout move deltas must be finite numbers.");
      }
      break;
    }
    case "layout.node.resize": {
      if (command.target.kind !== "layout-node") {
        push(errors, "invalid-target", "Layout resize must target a layout node.");
      }
      if (!Number.isFinite(command.payload.widthDelta) || !Number.isFinite(command.payload.heightDelta)) {
        push(errors, "out-of-range", "Layout resize deltas must be finite numbers.");
      }
      break;
    }
    case "layout.node.reorder": {
      if (command.target.kind !== "layout-node") {
        push(errors, "invalid-target", "Layout reorder must target a layout node.");
        break;
      }
      const node = draft.layoutNodes[command.target.id];
      if (!node || !node.parentId) {
        push(errors, "invalid-target", "Layout reorder requires a non-root layout node.");
        break;
      }
      const parent = draft.layoutNodes[node.parentId];
      if (!parent) {
        push(errors, "missing-entity", "Parent layout node was not found for reorder.");
        break;
      }
      if (command.payload.toIndex < 0 || command.payload.toIndex >= parent.childIds.length) {
        push(errors, "out-of-range", "Layout reorder target index is out of range.");
      }
      break;
    }
    case "widget.insert-from-prefab": {
      const slot = draft.slots[command.payload.slotId];
      if (!slot) {
        push(errors, "missing-entity", "Insert target slot does not exist.");
        break;
      }
      if (slot.widgetIds.length >= slot.maxWidgets) {
        push(errors, "slot-capacity-exceeded", "Slot capacity would be exceeded by prefab insertion.");
      }
      if (slot.acceptedWidgetTypes.length > 0 && !slot.acceptedWidgetTypes.includes(command.payload.prefab.widgetType)) {
        push(errors, "slot-incompatible", "Slot widget-type policy rejects the prefab.");
      }
      if (!command.payload.prefab.acceptedSlotKinds.includes(slot.kind)) {
        push(errors, "slot-incompatible", "Prefab slot-kind policy rejects the target slot.");
      }
      if (!command.payload.prefab.acceptedCapabilities.some((capability) => slot.acceptedCapabilities.includes(capability))) {
        push(errors, "slot-incompatible", "Slot capability policy rejects the prefab.");
      }
      break;
    }
    case "widget.update-props": {
      if (command.target.kind !== "widget") {
        push(errors, "invalid-target", "Widget prop updates must target a widget.");
      }
      break;
    }
    case "widget.update-style": {
      if (command.target.kind !== "widget") {
        push(errors, "invalid-target", "Widget style updates must target a widget.");
      }
      break;
    }
    case "widget.remove": {
      if (!draft.widgets[command.payload.widgetId]) {
        push(errors, "missing-entity", "Widget removal target does not exist.");
      }
      break;
    }
    case "selection.reset": {
      if (command.payload.baselineSceneId !== baseline.scene.id) {
        push(errors, "baseline-missing", "Selection reset requires the matching baseline scene.");
      }
      break;
    }
    default:
      break;
  }

  return { accepted: errors.length === 0, errors };
}
